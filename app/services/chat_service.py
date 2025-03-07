from typing import Any


class ChatService:
    def __init__(self, llm_client: Any):
        self.client = llm_client
        self.messages = [{"role": "system", "content": "You are a helpful assistant."}]

    def chat_completion(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        res = self.client.chat_completion(self.messages)
        self.messages.append({"role": "assistant", "content": "res"})
        return res
