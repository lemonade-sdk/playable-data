Each folder in this directory corresponds to a classic arcade-style game.

This README gives an overview of the folders and files, as well as the LLM prompts used to generate them.

## Directory Structure

These folders contain:
- A base game script, whose name matches the name of the folder (e.g., space_invaders/space_invaders.py).
- A few remix scripts, which use the base script as a starting point and then make some modification to the game.
- A few remixes-of-remixes.

## PyGame scripts
The format of each script is:
- For remix scripts only: Two single-line comments at the top:
  - `# SOURCE: filename.py` - The base script that generated this remix
  - `# REMIX: brief description` - A minimal prompt describing the remix
- A docstring that gives a brief description of the game and its mechanics from an implementation point of view.
- A complete implementation of a single game, written in Python and using `pygame` as the only external dependence.

## Prompts

### Base Game Prompt

This prompt can be used to generate the a base game. Replace `snake` with any game name. This prompt assumes an empty file named `snake.py` in a folder named `snake`.

```
Write the game Snake in Python using the pygame library. Place the code in @snake.py. 

Do not use any external image, audio, or other file assets. Everything needed should be in the one file.

When the game ends, the player should be able to restart the game by pressing R or quit by pressing Q. Pressing the "X" button on the game window should end the game at any time.

This script will be a reference design for an entry-level game design student, so make it as clear and concise as possible. Keep comments to a minimum, only to demarcate the most important sections of code or mechanics. 

Make the graphics minimal. Use black as the primary background color and rgb(0, 255, 65) as the primary accent color.

Add a docstring to the top of the file with the game's name and a very concise description of the mechanics and implementation from the programmer's point of view.
```

### Remix Prompt

This prompt can be used to remix a base game script. It is expected to be used in the same LLM chat that produced the base game, so that the base game is in context.

```
Great! Next, I want you to "remix" this game into a new file in the same folder.

Remix: make the food move to random adjacent positions on each update.

Add these comments at the very top of the file:
# SOURCE: snake.py
# REMIX: make the food move

The docstring of the new file should mention that this remix took place relative to the original game.
```

### Remix-of-Remix Prompts

> Note: these prompts assume you are in the same chat that produced the base game and initial remixes

To generate game scripts that contain two remix ideas:

```
ok great! now go through the space invaders remixes and make 5 new remix files

these new remixes should use one of the existing remix files as the base code, and apply one of the other remix ideas as a minimal modification on top of the base.

For each new file, add SOURCE and REMIX comments at the top:
# SOURCE: existing_remix_file.py
# REMIX: brief description of the new modification being added
```

To generate game scripts that have three remix ideas:

```
great! along the lines of the last exercise, make 4 files that contian 3 remix ideas. base these files on existing double-remix files.

For each new file, add SOURCE and REMIX comments at the top:
# SOURCE: existing_double_remix_file.py  
# REMIX: brief description of the third modification being added
```