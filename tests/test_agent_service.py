from app.config import settings
from app.infra import LLMProvider
from app.services import AgentService

llm_client = LLMProvider(
    base_url=settings.LLM_BASE_URL,
    api_key=settings.LLM_API_KEY,
    model=settings.LLM_MODEL,
)
agent_service = AgentService(llm_client=llm_client)


def test_chat_completion():
    prompt = "echo: this is a test"
    res = agent_service.chat_completion(prompt)
    assert "this is a test" in res.lower()
