from typing import Generator, List

import opuslib

from ..infra import ASRProvider, TTSProvider
from ..utils.audio import wav_to_opus


class AudioService:
    def __init__(self, asr_client: ASRProvider, tts_client: TTSProvider):
        self.asr_client = asr_client
        self.tts_client = tts_client

    def speech2text(self, opus_bytes: List[bytes]) -> str:
        decoder = opuslib.Decoder(16000, 1)  # 16000 sample rate and 1 channel
        pcm_frame = b""
        for piece in opus_bytes:
            pcm_frame += decoder.decode(piece, 960)
        return self.asr_client.speech2text(pcm_frame)

    def text2speech(
        self, text_stream: Generator[str, None, None]
    ) -> Generator[bytes, None, None]:
        audio_stream = self.tts_client.text2speech(text_stream)
        for wav_bytes in audio_stream:
            if wav_bytes is not None:
                yield from wav_to_opus(wav_bytes)
