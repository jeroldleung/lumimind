from typing import Generator, List

import opuslib

from ..infra import ASRProvider, TTSProvider, VADProvider
from ..utils.audio import wav_to_opus


class AudioService:
    def __init__(self, asr_client: ASRProvider, tts_client: TTSProvider):
        self.asr_client = asr_client
        self.vad_client = VADProvider()
        self.tts_client = tts_client
        self.fs = int(1 * 60 * 16000 / 1000)
        self.decoder = opuslib.Decoder(16000, 1)  # 16000 sample rate and 1 channel

    def speech2text(self, opus_bytes: List[bytes]) -> str:
        pcm_frame = self.decode(opus_bytes)
        return self.asr_client.speech2text(pcm_frame)

    def text2speech(self, text: str) -> Generator[bytes, None, None]:
        audio = self.tts_client.text2speech(text)
        yield from wav_to_opus(audio)

    def decode(self, opus_bytes: List[bytes]) -> bytes:
        pcm_frame = b""
        for piece in opus_bytes:
            pcm_frame += self.decoder.decode(piece, self.fs)
        return pcm_frame
