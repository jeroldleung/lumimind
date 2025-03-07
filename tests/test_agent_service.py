from app.config import settings
from app.infra import IOTProvider, LLMProvider
from app.services import AgentService

llm_client = LLMProvider(
    base_url=settings.LLM_BASE_URL,
    api_key=settings.LLM_API_KEY,
    model=settings.LLM_MODEL,
)
iot_client = IOTProvider(settings.IOT_SERVICE_URL)
agent_service = AgentService(llm_client, iot_client)


def test_tool_calling():
    instruction = "turn on the light"
    res = agent_service.chat_completion(instruction)
    assert res
