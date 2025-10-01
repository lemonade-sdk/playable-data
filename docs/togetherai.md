## Fine-Tune the model

1. Generate jsonl file: `python scripts/generate_dataset.py`
    1. This will produce `output/dataset.jsonl`
1. Go to https://api.together.ai/fine-tuning (make an account if needed)
    1. Fund the account with $5. This fine-tuning only costs $0.14.
1. Click `New Fine-Tuning Job`.
1. Select `Qwen/Qwen2.5-7B-Instruct` as the model.
1. Upload `output/dataset.jsonl` as the training data.
1. Add a suffix like `iat-00` (infinity-arcade-test-00).
1. Use default settings and click `Create Job` at the bottom.
1. Wait about 5 minutes, then download the merged checkpoint.
1. Unzip the checkpoint.
    1. We'll refer to this directory as `/path/to/model`

## Convert to GGUF for testing

1. conda create -n playable python=3.12
1. git clone https://github.com/ggerganov/llama.cpp.git
1. pip install -r llama.cpp/requirements.txt
1. pip install cmake
1. python llama.cpp/convert_hf_to_gguf.py /path/to/model
    1. We'll refer to this result as model-f16.gguf
1. cd llama.cpp
1. mkdir build
1. cd build
1. cmake .. -DLLAMA_CURL=OFF
1. cmake --build . --config Release
1. cd .\bin\Release\
1. ./llama-quantize path/to/model-f16.gguf path/to/model-q4_k_m.gguf Q4_K_M

## Upload to HF

1. Go to huggingface.co
1. Click your profile picture, then `+ Model`
1. Pick a checkpoint name like `Qwen2.5-7B-Instruct-iat-00-q4_k_m.gguf`
    1. We'll refer to this as `checkpoint`
    1. So the checkpoint's URL is `huggingface.co/user/checkpoint`
1. MIT license, private, create
1. Upload path/to/model-q4_k_m.gguf
    1. We'll refer to `model-q4_k_m.gguf` as such
    1. The `checkpoint:variant` for Lemonade will be `user/checkpoint:model-q4_k_m.gguf`

## Add to Lemonade

1. Start Lemonade, open the webui, go to Add a Model
    1. Model Name: `Qwen2.5-7B-Instruct-iat-00-GGUF`
    1. Checkpoint: `user/checkpoint:model-q4_k_m.gguf`
    1. Recipe: `llamacpp`

## Run in Infinity Arcade
1. Load up your Infinity Arcade environment
1. $env:INFINITY_ARCADE_MODEL="user.Qwen2.5-7B-Instruct-iat-00-GGUF"
1. infinity-arcade
1. Your new model should load during startup!
