import asyncio
import os
import signal

from loguru import logger
from websockets.asyncio.server import serve

from app.core.connection_handler import ConnectionHandler
from app.infra.asr_provider import ASRProvider
from app.infra.iot_provider import IOTProvider
from app.infra.llm_provider import LLMProvider
from app.infra.tts_provider import TTSProvider
from app.services.agent_service import AgentService
from app.services.audio_service import AudioService


class WebsocketServer:
    def __init__(self):
        self.host = os.environ["SERVER_HOST"]
        self.port = os.environ["SERVER_PORT"]

        # client initialize
        asr_client = ASRProvider(local_path=os.environ["ASR_LOCAL_PATH"])
        tts_client = TTSProvider(os.environ["TTS_API_KEY"], os.environ["TTS_MODEL"])
        llm_client = LLMProvider(
            base_url=os.environ["LLM_BASE_URL"],
            api_key=os.environ["LLM_API_KEY"],
            model=os.environ["LLM_MODEL"],
        )
        iot_client = IOTProvider(os.environ["IOT_SERVICE_URL"])

        # service initialize
        audio_service = AudioService(asr_client, tts_client)
        agent_service = AgentService(llm_client, iot_client)

        # singleton services are injected to connection handler
        ConnectionHandler.inject(audio_service, agent_service)

    async def start(self):
        async with serve(ConnectionHandler.instantiate, self.host, self.port) as server:
            logger.success("Server started")
            # Close the server when receiving SIGTERM and SIGINT.
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGTERM, server.close)
            loop.add_signal_handler(signal.SIGINT, server.close)
            await server.wait_closed()
            logger.success("Server closed")
