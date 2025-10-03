# Together.ai Fine-Tuning

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

> Note: See Appendix: Training Runs for more settings choices

## Convert to GGUF for testing

### Setup llama.cpp

1. conda create -n playable python=3.12
1. conda activate playable
1. git clone https://github.com/ggerganov/llama.cpp.git
1. pip install -r llama.cpp/requirements.txt
1. pip install cmake
1. cd llama.cpp
1. mkdir build
1. cd build
1. cmake .. -DLLAMA_CURL=OFF
1. cmake --build . --config Release

### Convert and Quantize

1. conda activate playable
1. cd llama.cpp/
1. python convert_hf_to_gguf.py /path/to/model
    1. We'll refer to this result as model-f16.gguf
1. cd build\bin\Release\
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

# Appendix: Training Runs

## iat-00

My first attempt. I used all the default together.ai fine-tuning settings.

The resulting model was a little better than the amd/qwen2.5-7b-instruct-...-hybrid I had been using, but not a lot better.

## iat-01

Based on advice from ChatGPT I made the following modifications:
1. Increased the number of base scripts, without remix edits, in the dataset by 5x.
1. Added markdown python wrappers to all code samples.
1. Applied the following fine-tuning settings:

```
Model:
Qwen/Qwen2.5-7B-Instruct
Training file:
dataset_01.jsonl
Suffix:
iat-01
Training type:
LoRA
LoRA rank:
32
LoRA alpha:
64
LoRA dropout:
0
LoRA trainable modules:
all-linear
Training method:
SFT
Train on inputs:
false
Epochs:
5
Checkpoints:
1
Evaluations:
1
Batch size:
8
Learning rate:
0.0001
Warmup ratio:
0.03
Max gradient norm:
1
Weight decay:
0
LR scheduler type:
cosine
Min LR ratio:
0.05
Scheduler cycles:
1
```

### Result

iat-01 showed an increased capability to handle space invaders and breakout, but struggled with pong and snake.

## iat-02

For this run we just tweaked the training settings relative to iat-01.

```
Model:
Qwen/Qwen2.5-7B-Instruct
Training file:
dataset_01.jsonl
Suffix:
iat-02
Training type:
LoRA
LoRA rank:
32
LoRA alpha:
64
LoRA dropout:
0.05
LoRA trainable modules:
all-linear
Training method:
SFT
Train on inputs:
false
Epochs:
5
Checkpoints:
1
Evaluations:
1
Batch size:
8
Learning rate:
0.00005
Warmup ratio:
0.03
Max gradient norm:
1
Weight decay:
0
LR scheduler type:
cosine
Min LR ratio:
0.05
Scheduler cycles:
1
```

### Result

- In pong the paddles are sideways.
- Snake works.
- Flappy bird and space invaders build with errors.
- Breakout works, and remixes work.

## iat-03

iat-03 uses the same parameters as iat-02, but greatly increases the amount of base games in the fine-tuning data.

The new base games were created by creating "oneshot" versions of the remix data previously available.

============================================================
DATASET STATISTICS
============================================================
Game Type            Count           Lines of Code
------------------------------------------------------------
Base Games           92              20,883
Remix Games          62              14,984
------------------------------------------------------------
TOTAL                154             35,867
============================================================

This dataset also fixes a bug where base game variants would have an index number in the prompt.

```
Model:
Qwen/Qwen2.5-7B-Instruct
Training file:
dataset_03.jsonl
Suffix:
iat-03
Training type:
LoRA
LoRA rank:
32
LoRA alpha:
64
LoRA dropout:
0.05
LoRA trainable modules:
all-linear
Training method:
SFT
Train on inputs:
false
Epochs:
5
Checkpoints:
1
Evaluations:
1
Batch size:
8
Learning rate:
0.00005
Warmup ratio:
0.03
Max gradient norm:
1
Weight decay:
0
LR scheduler type:
cosine
Min LR ratio:
0
Scheduler cycles:
1
```
