# Fine-Tuning on Fireworks AI

My jobs are getting stuck on "pending" status on together.ai, so I'm trying fireworks.ai.

## iat-03

Settings:

```
Output Model
iat-03

Base Model
qwen2p5-coder-7b

Type
Conversation
State
Validating
Created On
Friday, October 3, 2025
Status
Code
OK
Configuration
Dataset
dataset-03-jsonl

Evaluation Dataset
Auto-carve-out
Epochs
5
LoRA Rank
32
Learning Rate
0.0005
Max Context Length
8192
Turbo Mode
Off
```

Dataset:

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


### Validation

Training loss: 0.009
Evaluation loss: 0.03