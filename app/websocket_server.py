from loguru import logger
from websockets.asyncio.server import serve

from .config import settings
from .core.connection_handler import ConnectionHandler
from .infra import ASRProvider, IOTProvider, LLMProvider
from .services import AgentService, AudioService


class WebsocketServer:
    @staticmethod
    async def start():
        # client initialize
        asr_client = ASRProvider(local_path=settings.ASR_LOCAL_PATH)
        llm_client = LLMProvider(
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY,
            model=settings.LLM_MODEL,
        )
        iot_client = IOTProvider(settings.IOT_SERVICE_URL)

        # service initialize
        audio_service = AudioService(asr_client)
        agent_service = AgentService(llm_client, iot_client)

        # singleton services inject to handler
        ConnectionHandler.inject(audio_service, agent_service)

        async with serve(ConnectionHandler.instantiate, "0.0.0.0", 8000) as server:
            logger.success("Server started")
            await server.serve_forever()
