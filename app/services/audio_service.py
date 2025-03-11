import base64
from io import BytesIO
from typing import Generator

import numpy as np
import opuslib
import soundfile as sf
from pydub import AudioSegment

from app.infra import ASRProvider


class AudioService:
    def __init__(self, asr_client: ASRProvider):
        self.asr_client = asr_client

    def speech2text(self, opus_bytes: list[bytes]) -> str:
        decoder = opuslib.Decoder(16000, 1)  # 16000 sample rate and 1 channel
        pcm_frame = b""
        for piece in opus_bytes:
            pcm_frame += decoder.decode(piece, 960)
        return self.asr_client.speech2text(pcm_frame)

    def wav_to_opus(self, audio_str: str) -> Generator[bytes, None, None]:
        """Convert a base64-encoded wav audio string to an opus-encoded audio string."""
        wav_bytes = base64.b64decode(audio_str)  # decoded audio string to audio bytes
        audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
        wav_buf = BytesIO()
        sf.write(wav_buf, audio_np, samplerate=16000, format="wav")
        audio = AudioSegment.from_file(wav_buf, format="wav")  # load wav data
        audio.set_channels(1).set_frame_rate(16000)
        encoder = opuslib.Encoder(16000, 1, opuslib.APPLICATION_AUDIO)

        frame_duration = 60  # 60ms per frame
        frame_size = int(16000 * frame_duration / 1000)
        raw_data = audio.raw_data

        for i in range(0, len(raw_data), frame_size * 2):
            chunk = raw_data[i : i + frame_size * 2]
            if len(chunk) < frame_size * 2:
                chunk += b"\x00" * (frame_size * 2 - len(chunk))
            np_frame = np.frombuffer(chunk, dtype=np.int16)
            opus_data = encoder.encode(np_frame.tobytes(), frame_size)
            yield opus_data
