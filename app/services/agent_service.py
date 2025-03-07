from app.infra import LLMProvider


class AgentService:
    def __init__(self, llm_client: LLMProvider):
        self.llm_client = llm_client
        self.messages = [{"role": "system", "content": "You are a helpful assistant."}]

    def chat_completion(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        msg = self.llm_client.chat_completion(messages=self.messages)
        if msg.content is not None:
            self.messages.append({"role": "assistant", "content": msg.content})
            return msg.content
