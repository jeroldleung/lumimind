# lumimind

## Prerequisites

SenseVoice model

```bash
# Make sure you have git-lfs installed
git lfs install
git clone https://www.modelscope.cn/iic/SenseVoiceSmall.git pretrained_models/SenseVoiceSmall
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install uv
uv sync
uv run main.py
```