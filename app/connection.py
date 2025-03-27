import asyncio
import json

from loguru import logger
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed

from app.agent.qwen import Qwen
from app.asr.sensevoice import SenseVoice
from app.codec import Codec
from app.memory import Memory
from app.message import Message
from app.tts.cosyvoice import CosyVoice


class Connection:
    def __init__(self, conn: ServerConnection, asr: SenseVoice, agent: Qwen, tts: CosyVoice, codec: Codec):
        self.conn = conn
        self.asr = asr
        self.agent = agent
        self.mem = Memory()
        self.tts = tts
        self.codec = codec
        self.audio = b""
        self.queue = asyncio.Queue()

    async def consume(self):
        try:
            async for msg in self.conn:
                self.queue.put_nowait(msg)
        except ConnectionClosed:
            self.queue.shutdown()

    async def produce(self):
        while True:
            try:
                msg = await self.queue.get()
                if isinstance(msg, str):
                    await self._route(msg)
                    self.queue.task_done()
                elif isinstance(msg, bytes):
                    pcm = self.codec.decode(msg)
                    self.audio += pcm
            except asyncio.QueueShutDown:
                break

    async def _communicate(self):
        trans = self.asr.transcript(self.audio)  # transcript
        logger.debug(f"Transcription: {trans}")
        self.mem.add_user_msg(trans)
        comp = self.agent.chat(self.mem.get())  # chat completion
        logger.debug(f"Completion: {comp}")
        self.mem.add_assistant_msg(comp)
        await self.conn.send(Message.build_tts(state="sentence_start", text=comp))
        res = self.tts.synthesize(comp)  # tts
        await self.conn.send(Message.build_tts(state="start"))
        for chunk in self.codec.encode(res):
            await self.conn.send(chunk)
            await asyncio.sleep(self.codec.ms * 1e-3)
        await self.conn.send(Message.build_tts(state="stop"))

    async def _route(self, msg: str):
        logger.debug(f"Receive message {msg}")
        m = json.loads(msg)
        if m["type"] == "hello":
            await self.conn.send(Message.build_hello(sample_rate=self.codec.sample_rate))
        elif m["type"] == "listen":
            if m["state"] == "start":
                self.audio = b""
            elif m["state"] == "stop":
                if self.audio != b"":
                    await self._communicate()
