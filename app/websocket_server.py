from loguru import logger
from websockets.asyncio.server import serve

from .config import settings
from .core.connection_handler import ConnectionHandler
from .infra import ASRProvider, LLMProvider
from .services import AudioService, ChatService


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

        # service initialize
        audio_service = AudioService(asr_client)
        chat_service = ChatService(llm_client)

        # singleton services inject to handler
        ConnectionHandler.inject(audio_service, chat_service)

        async with serve(ConnectionHandler.instantiate, "0.0.0.0", 8000) as server:
            logger.success("Server started")
            await server.serve_forever()
