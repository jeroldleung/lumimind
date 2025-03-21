import os

from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess


class ASRProvider:
    def __init__(self, *, local_path: str):
        self.model = AutoModel(
            model=os.path.join(os.getcwd(), local_path),
            disable_update=True,
            disable_pbar=True,
        )

    def speech2text(self, audio_bytes: bytes) -> str:
        res = self.model.generate(input=audio_bytes)
        text = rich_transcription_postprocess(res[0]["text"])
        return text
