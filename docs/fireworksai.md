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

### Results

https://huggingface.co/playable/Qwen2.5-Coder-7B-Instruct-iat-03-GGUF

- Pong works, and can be remixed for accelerating ball and 2D movement
- Snake works, and remixing the food to move also works.
    - "snake but the food moves", "snake with two players" works in 1 shot!
- Flappy bird works, but remix doesnt
- Asteroids doesnt really work
- Space invaders worked, but my remix try didn't
- Games actually show "press R to restart or Q to quit"
- Breakout works
- Frequent "unmatched )" error
- Gaming fixing agent doesn't work well (not surprising since it isn't in the training set) 
- The \`\`\`python fencing sometimes ends up in the game code. Parsing error in arcade, or is the fencing getting repeated?
    -There's another fencing bug where some backticks are at the end of the game code.
    - Let's just remove the fencing from the training data?



### Next Steps

1. Remove markdown code fencing from the training data
1. Add game fixing to the training data
1. Adjust the prompts so that the game script is the only output of the LLM