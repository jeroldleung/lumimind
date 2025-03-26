import asyncio
import signal

from loguru import logger
from websockets.asyncio.server import serve

from .config import settings
from .core.connection_handler import ConnectionHandler
from .infra import ASRProvider, IOTProvider, LLMProvider, TTSProvider
from .services import AgentService, AudioService


class WebsocketServer:
    def __init__(self):
        self.host = settings.SERVER_HOST
        self.port = settings.SERVER_PORT

        # client initialize
        asr_client = ASRProvider(local_path=settings.ASR_LOCAL_PATH)
        tts_client = TTSProvider(settings.TTS_API_KEY, settings.TTS_MODEL)
        llm_client = LLMProvider(
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY,
            model=settings.LLM_MODEL,
        )
        iot_client = IOTProvider(settings.IOT_SERVICE_URL)

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
