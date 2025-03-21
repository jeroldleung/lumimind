from funasr import AutoModel


class VADProvider:
    def __init__(self):
        self.model = AutoModel(
            model="pretrained_models/speech_fsmn_vad_zh-cn-16k-common-pytorch",
            disable_update=True,
            disable_pbar=True,
        )
        self.chunk_size = 200
        self.cache = {}

    def reset(self):
        self.cache = {}
