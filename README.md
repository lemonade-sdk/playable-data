# Playable Data

A collection of high-quality retro-style pygame scripts useful for fine-tuning LLMs.

You can also play any game like this:

```
pip install pygame
python data/snake/snake.py
```

## Repo Structure

All data is stored in the [data/](data) folder. See the [README.md](data/README.md) there for details about the data.

Run `python scripts/generate_dataset.py` to generate a `output\dataset.json` file containing instruct-formatted fine-tuning data.

`docs/` folder contains guides (WIP) for running fine-tuning.

## Results

This README will be updated over time with the results of fine-tuning experiments, links to models, etc.

## License

The goal of this repo is to support fine-tuning models for use with [Infinity Arcade](https://github.com/lemonade-sdk/infinity-arcade), however the dataset is publicly available for anyone to use under the [MIT license](LICENSE). Please note that the data was generated using Anthropic Claude models in Cursor, so the licenses of those products also apply to the data.

## Maintainer

This project is maintained by @jeremyfowers. It is sponsored by AMD.
