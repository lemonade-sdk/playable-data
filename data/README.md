Each folder in this directory corresponds to a classic arcade-style game.

This README gives an overview of the folders and files, as well as the LLM prompts used to generate them.

## Directory Structure

These folders contain:
- A base game script, whose name matches the name of the folder (e.g., space_invaders/space_invaders.py).
- Multiple base game variants (e.g., asteroids_1.py, asteroids_2.py, etc.) - different implementations of the same base game with varied coding styles, visual choices, and game balance.
- A few remix scripts, which use the base script as a starting point and then make some modification to the game.
- A few remixes-of-remixes.
- Oneshot scripts (ending in `_oneshot.py`) - standalone versions of remix games that can be created from a single prompt without requiring a base game.

> Note: an underscore `_` in the directory name indicates that the directory should be skipped. This is useful for game data that is not fully ready yet.

## PyGame scripts
The format of each script is:
- For remix scripts only: Two single-line comments at the top:
  - `# SOURCE: filename.py` - The base script that generated this remix
  - `# REMIX: brief description` - A minimal prompt describing the remix
- For base/variant/oneshot scripts: One single-line comment at the top:
  - `# CREATE: brief description` - A minimal prompt describing the game to create
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

### Base Game Variants Prompt

This prompt creates multiple variant implementations of a base game, simulating different student solutions to the same assignment. Each variant uses the same core OOP approach but differs in natural ways. Replace `snake` with any game name.

```
I need you to create 4 additional variants of the Snake game (<game>_1.py through <game>_4.py). These should feel like 4 different students all attended the same class, learned the same OOP principles, and completed the same homework assignment to make this game in pygame.

All variants must:
- Follow the base game rules (black background, green color rgb(0, 255, 65), R to restart, Q to quit, X to close)
- Use object-oriented design with classes for the main game entities
- Be clear and understandable for entry-level game design students
- Include a docstring describing the game

Vary these details naturally across the 4 variants (like different students would):

1. Variable/function naming conventions
   - Different naming styles within snake_case convention
   - Method names: update() vs move() vs advance() vs tick()
   - Class attribute names reflecting personal preference

2. Visual representation choices
   - Shape/rendering differences for game entities
   - Screen dimensions (e.g., 800x600 vs 600x600 vs 900x700)
   - Size and proportions of game elements

3. Code organization
   - Some put all constants at top, others define near usage
   - Different method ordering (alphabetical vs logical grouping)
   - Varying levels of helper functions vs inline code

4. Game balance/tuning
   - Different starting conditions and difficulty parameters
   - Speed, acceleration, or movement values
   - Scoring systems and point values
   - Spawn rates, quantities, or timing

5. Minor mechanic differences
   - Input handling variations (continuous vs discrete)
   - Different values for friction, drag, or damping
   - Alternative collision detection approaches (all achieving same result)
   - Edge behavior variations (wrap vs bounce, when applicable)

Example for Asteroids specifically: Ship could be triangle vs diamond shape, asteroids as circles vs irregular polygons, starting with 3-6 asteroids, one shot per press vs continuous fire with cooldown, scoring as size*20 vs (4-tier)*15.

Make each variant feel authentic - like a real student's work with their own preferences and interpretations, but all demonstrating good OOP practices.
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

### Oneshot Game Prompt

Oneshot scripts are standalone versions of remix games that can be created from a single prompt without requiring a base game. They have a `# CREATE:` comment at the top and contain the complete game code.

```
Create a game: asteroids with rainbow colors where I can press enter to blast the asteroids near the ship

[The LLM would generate the complete game code with appropriate CREATE comment and standalone docstring]
```

Oneshot scripts are useful for:
- Training models to generate complete games from single prompts
- Creating standalone game variants without dependency chains
- Demonstrating specific game mechanics in isolation
