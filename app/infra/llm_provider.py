from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


class LLMProvider:
    def __init__(self, *, base_url: str, api_key: str, model: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def chat_completion(self, messages: list[ChatCompletionMessageParam]) -> str:
        completion = self.client.chat.completions.create(
            model=self.model, messages=messages
        )
        res = completion.choices[0].message.content
        return res
