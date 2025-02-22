import base64
import json
import os
from io import BytesIO
from typing import Generator

import numpy as np
import opuslib
import soundfile as sf
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment
from websockets.sync.server import ServerConnection, serve


def wav_to_opus(audio_str: str) -> Generator[bytes, None, None]:
    """Convert a base64-encoded wav audio string to an opus-encoded audio string."""
    wav_bytes = base64.b64decode(audio_str)  # decoded audio string to audio bytes
    audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
    wav_buf = BytesIO()
    sf.write(wav_buf, audio_np, samplerate=16000, format="wav")
    audio = AudioSegment.from_file(wav_buf, format="wav")  # load wav data
    audio.set_channels(1).set_frame_rate(16000)
    encoder = opuslib.Encoder(16000, 1, opuslib.APPLICATION_AUDIO)

    frame_duration = 60  # 60ms per frame
    frame_size = int(16000 * frame_duration / 1000)  # 960 samples/frame
    raw_data = audio.raw_data

    for i in range(0, len(raw_data), frame_size * 2):
        chunk = raw_data[i : i + frame_size * 2]
        if len(chunk) < frame_size * 2:
            chunk += b"\x00" * (frame_size * 2 - len(chunk))
        np_frame = np.frombuffer(chunk, dtype=np.int16)
        opus_data = encoder.encode(np_frame.tobytes(), frame_size)
        yield opus_data


def chat(websocket: ServerConnection):
    client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))
    memory = [{"role": "system", "content": "You are a helpful assistant."}]

    def handshake():
        to_device = {
            "type": "hello",
            "transport": "websocket",
            "audio_params": {"sample_rate": 16000},
        }
        websocket.send(json.dumps(to_device))

    def stream_llm_output():
        memory.append({"role": "user", "content": "你好"})
        for chunk in client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=memory,
            modalities=["text", "audio"],
            audio={"voice": "Cherry", "format": "wav"},
            stream=True,
        ):
            if not hasattr(chunk.choices[0].delta, "audio"):
                continue
            if "data" in chunk.choices[0].delta.audio:
                audio_str = chunk.choices[0].delta.audio["data"]
                for piece in wav_to_opus(audio_str):
                    websocket.send(piece)

    while True:
        msg = websocket.recv()
        print(msg)
        if isinstance(msg, str):
            msg = json.loads(msg)
            if msg["type"] == "hello":
                handshake()
            elif msg["type"] == "listen":
                if msg["state"] == "stop":
                    message = {"type": "tts", "state": "start", "text": ""}
                    websocket.send(json.dumps(message))
                    stream_llm_output()
                    message = {"type": "tts", "state": "stop", "text": ""}
                    websocket.send(json.dumps(message))


def main():
    with serve(chat, "0.0.0.0", 8000) as server:
        server.serve_forever()


if __name__ == "__main__":
    assert load_dotenv(), "Failed to load environment variables"
    main()
