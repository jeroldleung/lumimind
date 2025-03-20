import os

from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess


class VADProvider:
    def __init__(self):
        self.model = AutoModel(
            model="pretrained_models/speech_fsmn_vad_zh-cn-16k-common-pytorch",
            disable_update=True,
        )
