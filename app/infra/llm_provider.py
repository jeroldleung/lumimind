from typing import List

from openai import OpenAI, pydantic_function_tool
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)
from pydantic import BaseModel


class LLMProvider:
    def __init__(self, *, base_url: str, api_key: str, model: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.tools: List[ChatCompletionToolParam] = []

    def registry_tools(self, tools: List[BaseModel]):
        for t in tools:
            self.tools.append(pydantic_function_tool(t))

    def chat_completion(
        self, messages: List[ChatCompletionMessageParam]
    ) -> ChatCompletion:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
        )
        return completion
