import asyncio
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from websockets.asyncio.server import serve


async def stream_llm_response(websocket: Any, client: OpenAI, messages: list[str]):
    response = ""
    for chunk in client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=messages,
        modalities=["text"],
        stream=True,
    ):
        text = chunk.choices[0].delta.content
        if text is not None:
            await websocket.send(text)
            response += text
    return response


async def chat(websocket: Any):
    llm_client = OpenAI(
        base_url=os.getenv("LLM_BASE_URL"),
        api_key=os.getenv("LLM_API_KEY"),
    )
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    async for msg in websocket:
        messages.append({"role": "user", "content": msg})
        response = await stream_llm_response(websocket, llm_client, messages)
        messages.append({"role": "assistant", "content": response})


async def main():
    async with serve(chat, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    assert load_dotenv(), "Failed to load environment variables"
    asyncio.run(main())
