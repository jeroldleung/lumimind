import os
from typing import Generator

from openai import OpenAI

client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))
messages = [{"role": "system", "content": "You are a helpful assistant."}]


def stream_llm_output(user_input: str) -> Generator[str, None, str]:
    response_text = ""
    messages.append({"role": "user", "content": user_input})
    for chunk in client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages,
        modalities=["text", "audio"],
        audio={"voice": "Cherry", "format": "wav"},
        stream=True,
    ):
        if hasattr(chunk.choices[0].delta, "audio"):
            if "data" in chunk.choices[0].delta.audio:
                audio_str = chunk.choices[0].delta.audio["data"]
                yield audio_str
            elif "transcript" in chunk.choices[0].delta.audio:
                text = chunk.choices[0].delta.audio["transcript"]
                response_text += text

    messages.append({"role": "assistant", "content": response_text})
    return response_text
