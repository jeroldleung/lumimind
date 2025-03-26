import asyncio
import os
import signal

from loguru import logger
from websockets.asyncio.server import serve

from app.agent.qwen import Qwen
from app.asr.sensevoice import SenseVoice
from app.connection import Connection
from app.agent.iot import IOTProvider
from app.services.agent_service import AgentService
from app.services.audio_service import AudioService
from app.tts.cosyvoice import CosyVoice


class Server:
    def __init__(self):
        self.host = os.environ["SERVER_HOST"]
        self.port = os.environ["SERVER_PORT"]

        # client initialize
        asr_client = SenseVoice()
        tts_client = CosyVoice()
        llm_client = Qwen()
        iot_client = IOTProvider(os.environ["IOT_SERVICE_URL"])

        # service initialize
        audio_service = AudioService(asr_client, tts_client)
        agent_service = AgentService(llm_client, iot_client)

        # singleton services are injected to connection handler
        Connection.inject(audio_service, agent_service)

    async def start(self):
        async with serve(Connection.instantiate, self.host, self.port) as server:
            logger.success("Server started")
            # Close the server when receiving SIGTERM and SIGINT.
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGTERM, server.close)
            loop.add_signal_handler(signal.SIGINT, server.close)
            await server.wait_closed()
            logger.success("Server closed")
