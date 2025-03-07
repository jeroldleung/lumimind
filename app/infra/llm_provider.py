from openai import OpenAI, pydantic_function_tool
from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)


class LLMProvider:
    def __init__(self, *, base_url: str, api_key: str, model: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.tools: list[ChatCompletionToolParam] = []

    def registry_tools(self, tools: list[ChatCompletionToolParam]):
        for t in tools:
            self.tools.append(pydantic_function_tool(t))

    def chat_completion(
        self, messages: list[ChatCompletionMessageParam]
    ) -> ChatCompletionMessage:
        completion = self.client.chat.completions.create(
            model=self.model, messages=messages, tools=self.tools
        )
        res = completion.choices[0].message
        return res
