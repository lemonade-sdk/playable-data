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

```
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
```

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

1. Remove markdown code fencing from the training data OR set temperature=0.3 and top_p=0.9 in the app
1. Add game fixing to the training data
1. Adjust the prompts so that the game script is the only output of the LLM

## iat-04

This is the first model to include bug/fix data in the training set.

### LORA Settings

Output Model
iat-04

Base Model
qwen2p5-coder-7b-instruct

Type
Conversation
State
Validating
Created On
Tuesday, October 7, 2025
Status
Code
OK
Configuration
Dataset
dataset-04-jsonl

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

Dataset:

```
============================================================
DATASET STATISTICS
============================================================
Game Type            Count           Lines of Code
------------------------------------------------------------
Base Games           92              20,883
Remix Games          62              14,984
Bug Fix Games        30              5,941
------------------------------------------------------------
TOTAL                184             41,808
============================================================
```

### Validation

Training loss: 0.009
Evaluation loss: 0.02

### Results


- The 4 bugs I've seen so far were not fixed.
    - The 5th-7th bugs were debugged properly, so perhaps a fluke.
- Pong has trouble - missing midline, ball doesn't move. 3rd attempt worked. 4th attempt the ball fell through the floor.
    - "BUG FIX" docstring shows up from all game creation prompts.
    - "move in 2d' remix didnt work
- Snake works great: remix moving food -> color changing food worked. Adding a third acceleration remix didnt work. 
    - One shotting acceleration doesnt work either.
    - "snake with an enemy that chases me" worked. 
    - "2 player snake" worked, except that the game doesnt end if player 2 dies
- Space invaders works. Rainbow colors remix worked. Oneshotting rainbow space invaders worked. Adding explosions to that worked.
- Flappy bird works. Add coins remix works, and then remixed realistic looking bird into that, and then "make the bird purple" into that.
- "Q to quit and R to restart" is working on all games!
- Breakout works, and "let the paddle move in 2d" remix worked.
    - "add another ball every 5 seconds" didnt work, but only because it messed up the unit mof time to be too long. 
- Asteroids almost works, but not quite.

### Next steps

1. Make sure arcade system and user prompts match generate_dataset.py prompts, which in turn match how the LLM is being called.
2. Remove BUG_FIX examples from pong. Pong rarely has bugs anyways.
    - Or, remove Pong from the dataset entirely? The base model can do pong just fine.
3. Figure out something to do about asteroids.