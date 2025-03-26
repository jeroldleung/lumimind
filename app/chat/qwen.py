import os
from typing import List

from openai import OpenAI, pydantic_function_tool
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)
from pydantic import BaseModel


class Qwen:
    def __init__(self):
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        api_key = os.environ["ALIYUN_API_KEY"]
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = os.environ["ALIYUN_LLM_MODEL"]
        self.tools: List[ChatCompletionToolParam] = []

    def registry_tools(self, tools: List[BaseModel]):
        for t in tools:
            self.tools.append(pydantic_function_tool(t))

    def chat_completion(self, messages: List[ChatCompletionMessageParam]) -> ChatCompletion:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
        )
        return completion
