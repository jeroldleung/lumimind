import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel

assert load_dotenv(), "Failed to load environment variables"

app = FastAPI(title="Liiaa")


class Prompt(BaseModel):
    content: str


async def stream_llm_response(prompt: Prompt, client: OpenAI):
    for chunk in client.chat.completions.create(
        model="qwen-omni-turbo",
        messages=[{"role": "user", "content": prompt.content}],
        modalities=["text"],
        stream=True,
    ):
        text = chunk.choices[0].delta.content
        if text is not None:
            yield text


@app.post("/stream")
async def chat(prompt: Prompt):
    llm_client = OpenAI(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
    )

    return StreamingResponse(
        stream_llm_response(prompt, llm_client),
        media_type="text/event-stream",
    )
