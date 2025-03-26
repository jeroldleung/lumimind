import json

from loguru import logger
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed

from app.asr.sensevoice import SenseVoice
from app.chat.qwen import Qwen
from app.codec import Codec
from app.memory import Memory
from app.tts.cosyvoice import CosyVoice


class Connection:
    def __init__(self, conn: ServerConnection, asr: SenseVoice, chat: Qwen, tts: CosyVoice, codec: Codec):
        self.conn = conn
        self.asr = asr
        self.chat = chat
        self.mem = Memory()
        self.tts = tts
        self.codec = codec
        self.audio = b""

    async def handle(self, msg: str):
        logger.debug(f"Receive message {msg}")
        m = json.loads(msg)
        if m["type"] == "hello":
            await self.conn.send(json.dumps({"type": "hello", "transport": "websocket"}))
        elif m["type"] == "listen":
            if m["state"] == "start":
                self.audio = b""
            elif m["state"] == "stop":
                if self.audio != b"":
                    trans = self.asr.transcript(self.audio)  # transcript
                    logger.debug(f"Transcription: {trans}")
                    self.mem.add_user_msg(trans)
                    comp = self.chat.completion(self.mem.get())  # chat completion
                    logger.debug(f"Completion: {comp}")
                    self.mem.add_assistant_msg(comp)
                    await self.conn.send(json.dumps({"type": "tts", "state": "sentence_start", "text": comp}))
                    res = self.tts.synthesize(comp)  # tts
                    await self.conn.send(json.dumps({"type": "tts", "state": "start", "sample_rate": self.sample_rate}))
                    stream = self.codec.wav_to_opus(res)
                    for chunk in stream:
                        await self.conn.send(chunk)
                    await self.conn.send(json.dumps({"type": "tts", "state": "stop"}))

    async def route(self):
        try:
            async for msg in self.conn:
                if isinstance(msg, str):
                    await self.handle(msg)
                elif isinstance(msg, bytes):
                    pcm = self.codec.decode(msg)
                    self.audio += pcm
        except ConnectionClosed:
            logger.info(f"Close connection {self.conn.id}")

