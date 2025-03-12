from typing import List

from loguru import logger
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed

from ..schemas.iot_message_schemas import AudioState, MessageIn, MessageOut, MessageType
from ..services import AgentService, AudioService


class ConnectionHandler:
    audio_service: AudioService | None = None
    agent_service: AgentService | None = None

    def __init__(self, websocket: ServerConnection):
        self.websocket = websocket
        self.audio_in: List[bytes] = []

    async def response_text(self, m_out: MessageOut):
        m_out = m_out.model_dump_json(exclude_unset=True)
        await self.websocket.send(m_out)

    async def handle_text(self, m_in: str):
        logger.debug(f"Message in: {m_in}")
        m = MessageIn.model_validate_json(m_in)

        # handshake with the client
        if m.type == MessageType.HELLO:
            await self.response_text(
                MessageOut(
                    type=MessageType.HELLO,
                    transport="websocket",
                    audio_params={"sample_rate": 16000},
                )
            )
            logger.info("Handshake with the client")

        # capture opus bytes from the device
        elif m.type == MessageType.LISTEN and m.state == AudioState.START:
            self.audio_in.clear()

        # response to the client
        elif m.type == MessageType.LISTEN and m.state == AudioState.STOP:
            if len(self.audio_in) == 0:
                return
            asr_text = ConnectionHandler.audio_service.speech2text(self.audio_in)
            logger.info(f"Client audio message: {asr_text}")
            chat_completion = ConnectionHandler.agent_service.chat_completion(asr_text)
            await self.response_text(
                MessageOut(
                    type=MessageType.TTS,
                    state=AudioState.SENTENCE_START,
                    text=chat_completion,
                )
            )
            logger.info(f"Response to client: {chat_completion}")

    async def handle_binary(self, m_in: bytes):
        self.audio_in.append(m_in)

    async def handle_message(self):
        while True:
            try:
                m_in = await self.websocket.recv()
                if isinstance(m_in, str):
                    await self.handle_text(m_in)
                elif isinstance(m_in, bytes):
                    await self.handle_binary(m_in)
            except ConnectionClosed:
                break

    @classmethod
    def inject(cls, audio_service: AudioService, agent_service: AgentService):
        cls.audio_service = audio_service
        cls.agent_service = agent_service

    @staticmethod
    async def instantiate(websocket: ServerConnection):
        if ConnectionHandler.audio_service is None:
            logger.error("Audio Service is not injected")
        print(ConnectionHandler.agent_service)
        if ConnectionHandler.agent_service is None:
            logger.error("Chat Service is not injected")

        # create a handler instance for each websocket connection
        logger.info(f"Connection opened: {websocket.id}")
        connection = ConnectionHandler(websocket)
        await connection.handle_message()
        logger.info(f"Connection closed: {websocket.id}")
