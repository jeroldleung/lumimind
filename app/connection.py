from typing import Generator, List

from loguru import logger
import opuslib
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed

from app.asr.sensevoice import SenseVoice
from app.schemas.iot_message_schemas import (
    AudioState,
    MessageIn,
    MessageOut,
    MessageType,
)
from app.services.agent_service import AgentService
from app.services.audio_service import AudioService


class Connection:
    audio_service: AudioService | None = None
    agent_service: AgentService | None = None

    def __init__(self, conn: ServerConnection, asr: SenseVoice):
        self.conn = conn
        self.asr = asr
        self.audio = b""
        self.sample_rate = 16000
        self.channel = 1
        self.ms = 60
        self.fs = int(self.channel * self.ms * self.sample_rate / 1000)
        self.dec = opuslib.Decoder(self.sample_rate, self.channel)
        

    async def response_text(self, m_out: MessageOut):
        m_out = m_out.model_dump_json(exclude_unset=True)
        await self.conn.send(m_out)

    async def response_audio(self, audio_stream: Generator[bytes, None, None]):
        m_out = MessageOut(type=MessageType.TTS, state=AudioState.START)
        await self.response_text(m_out)
        n_wait_ms = 0
        for audio_bytes in audio_stream:
            n_wait_ms += 1
            await self.conn.send(audio_bytes)
        m_out = MessageOut(type=MessageType.TTS, state=AudioState.STOP)
        await self.response_text(m_out)

    async def handle_text(self, m_in: str):
        logger.debug(f"Message in: {m_in}")
        m = MessageIn.model_validate_json(m_in)

        # handshake with the client
        if m.type == MessageType.HELLO:
            m_out = MessageOut(
                type=MessageType.HELLO,
                transport="websocket",
                audio_params={"sample_rate": 16000},
            )
            await self.response_text(m_out)
            logger.info("Handshake with the client")

        elif m.type == MessageType.LISTEN:
            # capture opus bytes from the device
            if m.state == AudioState.START:
                self.audio = b""
            elif m.state == AudioState.DETECT:
                pass
            elif m.state == AudioState.STOP:
                # response to the client
                if self.audio == b"":
                    return
                asr_text = self.asr.transcript(self.audio)
                logger.info(f"Client audio message: {asr_text}")
                chat_completion = await Connection.agent_service.chat_completion(self.conn, asr_text)
                m_out = MessageOut(
                    type=MessageType.TTS,
                    state=AudioState.SENTENCE_START,
                    text=chat_completion,
                )
                await self.response_text(m_out)
                logger.info(f"Response to client: {chat_completion}")
                audio_stream = Connection.audio_service.text2speech(chat_completion)
                await self.response_audio(audio_stream)


    async def route(self):
        Connection.agent_service.messages = Connection.agent_service.messages[:1]
        while True:
            try:
                m_in = await self.conn.recv()
                if isinstance(m_in, str):
                    await self.handle_text(m_in)
                elif isinstance(m_in, bytes):
                    pcm = self.dec.decode(m_in, self.fs)
                    self.audio += pcm
            except ConnectionClosed:
                break

    @classmethod
    def inject(cls, audio_service: AudioService, agent_service: AgentService):
        cls.audio_service = audio_service
        cls.agent_service = agent_service
