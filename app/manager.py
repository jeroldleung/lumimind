import os

from loguru import logger
from websockets.asyncio.server import ServerConnection

from app.asr.sensevoice import SenseVoice
from app.chat.iot import IOTProvider
from app.chat.qwen import Qwen
from app.connection import Connection
from app.services.agent_service import AgentService
from app.services.audio_service import AudioService
from app.tts.cosyvoice import CosyVoice


class Manager:
    def __init__(self):
        self.asr = SenseVoice()
        self.chat = Qwen()
        self.tts = CosyVoice()
        self.iot = IOTProvider(os.environ["IOT_SERVICE_URL"])

        # service initialize
        audio_service = AudioService(self.asr, self.tts)
        agent_service = AgentService(self.chat, self.iot)

        # singleton services are injected to connection handler
        Connection.inject(audio_service, agent_service)

    async def handle(self, conn: ServerConnection):
        logger.info(f"Open connection {conn.id}")
        c = Connection(conn)
        await c.route()
        logger.info(f"Close connection {conn.id}")
