from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess


class SenseVoice:
    def __init__(self):
        self.model = AutoModel(model="pretrained_models/SenseVoiceSmall", disable_update=True, disable_pbar=True)

    def transcript(self, audio: bytes) -> str:
        res = self.model.generate(input=audio)
        text = rich_transcription_postprocess(res[0]["text"])
        return text
