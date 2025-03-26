import os
from typing import Dict, List

from openai import OpenAI


class Qwen:
    def __init__(self):
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        api_key = os.environ["ALIYUN_API_KEY"]
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = os.environ["ALIYUN_LLM_MODEL"]

    def completion(self, messages: List[Dict]) -> str:
        completion = self.client.chat.completions.create(model=self.model, messages=messages)
        return completion.choices[0].message.content
