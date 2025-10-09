# Playable Data

A collection of high-quality retro-style pygame scripts useful for fine-tuning LLMs.

The goal of this repo is to support fine-tuning models for use with [Infinity Arcade](https://github.com/lemonade-sdk/infinity-arcade), however the data and models are provided as open-source software other use as well (see [License](#license)).

You can also play any game like this:

```
pip install pygame
python data/snake/snake.py
```

### Results

`playable-data` has been used to train a few models on together.ai so far. Detailed instructions and notes are available [here](docs/togetherai.md).

- All models will be uploaded at https://huggingface.co/playable.
- Models are named `-iat-XX`, where iat stands for Infinity Arcade Test, and XX is the test number.
- `Qwen2.5-7B-Instruct` (or `Qwen2.5-Coder-7B-Instruct`) is used as the base model because the intention is to eventually export for use on AMD NPUs, and Qwen2.5-7B-Instruct is one of the supported architectures for AMD NPUs.

| Model | Description |
|-------|-------------|
| [iat-01](https://huggingface.co/playable/Qwen2.5-7B-Instruct-iat-01) | The first 7B model I've been able to code Space Invaders with, but it struggles with basic games like Snake and Pong that the base model can handle easily. |
| [iat-02](https://huggingface.co/playable/Qwen2.5-7B-Instruct-iat-02) | Fixes Snake, but Pong is still broken. Breakout works! |
| [iat-03](https://huggingface.co/playable/Qwen2.5-Coder-7B-Instruct-iat-03-GGUF) | Switched to Qwen2.5-Coder as the base model and got Breakout and more remixes to work, but rough edges remain |
| [iat-04](https://huggingface.co/playable/Qwen2.5-Coder-7B-Instruct-iat-04-GGUF) | Added debugging examples to the dataset. Space Invaders now works! |
| [iat-05](https://huggingface.co/playable/Qwen2.5-Coder-7B-Instruct-iat-04-GGUF) | Added Galaga examples to the dataset and fixed prompt bugs. Galaga doesn't work though. |
| iat-05-01 | Changed training parameters. Galaga works! Released as https://huggingface.co/playable/Playable1-GGUF ! |

### Dataset Stats

The data, which is described in detail [here](data/README.md), is a collection of Python scripts that each implement a retro-style arcade game using only Python and the pygame library.

Each script has some metadata at the top in comments for things like the intended vibe coding prompt.

There are two types of games in the dataset right now:
- Base Games: one-shot vibe coding of a game.
- Remix Games: multi-shot vibe coding refinement of games.

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

## Repo Structure

All data is stored in the [data/](data) folder. See the [README.md](data/README.md) there for details about the data.

Run `python scripts/generate_dataset.py` to generate a `output\dataset.json` file containing instruct-formatted fine-tuning data.

`docs/` folder contains guides (WIP) for running fine-tuning.

## Contributions

This repo is still under heavy development, so its not time for contributions yet. Advice and requests in the issues are much appreciated, though!

## License

This dataset is publicly available for anyone to use under the [MIT license](LICENSE). Please note that the data (pygame scripts) was generated using Anthropic Claude models in Cursor, so the licenses of those products also apply to the data.

## Maintainer

This project is maintained by @jeremyfowers.
