import os

from loguru import logger
from websockets.asyncio.server import ServerConnection

from app.asr.sensevoice import SenseVoice
from app.chat.iot import IOTProvider
from app.chat.qwen import Qwen
from app.connection import Connection
from app.services.agent_service import AgentService
from app.tts.cosyvoice import CosyVoice


class Manager:
    def __init__(self):
        self.asr = SenseVoice()
        self.chat = Qwen()
        self.tts = CosyVoice()
        self.iot = IOTProvider(os.environ["IOT_SERVICE_URL"])

        # service initialize
        agent_service = AgentService(self.chat, self.iot)

        # singleton services are injected to connection handler
        Connection.inject(agent_service)

    async def handle(self, conn: ServerConnection):
        logger.info(f"Open connection {conn.id}")
        c = Connection(conn, self.asr, self.tts)
        await c.route()
        logger.info(f"Close connection {conn.id}")
