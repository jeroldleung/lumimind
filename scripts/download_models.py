from modelscope import snapshot_download

snapshot_download("iic/SenseVoiceSmall", local_dir="pretrained_models/SenseVoiceSmall")
snapshot_download("iic/speech_fsmn_vad_zh-cn-16k-common-pytorch", local_dir="pretrained_models/speech_fsmn_vad_zh-cn-16k-common-pytorch")
