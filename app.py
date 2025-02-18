import asyncio
import base64
import os
from typing import Any

import numpy as np
import pyaudio
from dotenv import load_dotenv
from openai import OpenAI
from websockets.asyncio.server import serve


async def stream_llm_response(
    websocket: Any, audio_stream: pyaudio.Stream, client: OpenAI, messages: list[str]
):
    response = ""
    for chunk in client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=messages,
        modalities=["text", "audio"],
        audio={"voice": "Cherry", "format": "wav"},
        stream=True,
    ):
        # decode base64 and play it
        if hasattr(chunk.choices[0].delta, "audio"):
            try:
                audio_string = chunk.choices[0].delta.audio["data"]
                wav_bytes = base64.b64decode(audio_string)
                audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
                audio_stream.write(audio_np.tobytes())
            except Exception:
                text = chunk.choices[0].delta.audio["transcript"]
                response += text
                await websocket.send(text)

    return response


async def chat(websocket: Any):
    llm_client = OpenAI(
        base_url=os.getenv("LLM_BASE_URL"),
        api_key=os.getenv("LLM_API_KEY"),
    )

    # play audio on the current device
    p = pyaudio.PyAudio()
    audio_stream = p.open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    async for msg in websocket:
        messages.append({"role": "user", "content": msg})
        response = await stream_llm_response(
            websocket, audio_stream, llm_client, messages
        )
        messages.append({"role": "assistant", "content": response})

    # release resources
    audio_stream.stop_stream()
    audio_stream.close()
    p.terminate()


async def main():
    async with serve(chat, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    assert load_dotenv(), "Failed to load environment variables"
    asyncio.run(main())
