from app.infra import LLMProvider


class AgentService:
    def __init__(self, llm_client: LLMProvider):
        self.llm_client = llm_client
        self.messages = [{"role": "system", "content": "You are a helpful assistant."}]

    def chat_completion(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        res = self.llm_client.chat_completion(self.messages)
        self.messages.append({"role": "assistant", "content": "res"})
        return res
