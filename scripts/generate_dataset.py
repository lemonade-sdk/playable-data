"""
This script takes the pygame scripts from the data directory and formats them
into an alpaca instruct json file.
"""

import json
from pathlib import Path

def format_create_game(script_content: str, create_prompt: str):
    """
    Format a create game script into instruct data.

    Args:
        script_content: The content of the script file
        create_prompt: The game name/prompt (filename without extension, underscores as spaces)
    """
    content = create_prompt

    create_instructions = """You are an expert Python game developer. Generate a complete, working Python game using pygame based on the user's description.

    Rules:
    1. Use ONLY the pygame library - no external images, sounds, or files
    2. Create everything (graphics, colors, shapes) using pygame's built-in drawing functions
    3. Make the game fully playable and fun
    4. Include proper game mechanics (win/lose conditions, scoring if appropriate)
    5. Use proper pygame event handling and game loop
    6. Add comments explaining key parts of the code
    7. Make sure the game window closes properly when the user clicks the X button
    8. Use reasonable colors and make the game visually appealing with pygame primitives

    Generate ONLY the Python code wrapped in a markdown code block using triple backticks (```python). Do not include any explanations outside the code block."""

    create_input = f"Create a game: {content}"

    return {
        "instruction": create_instructions,
        "input": create_input,
        "output": script_content
    }

def format_remix_game(script_content: str, base_game_content: str, remix_prompt: str):
    """
    Format a remix script into instruct data.

    Args:
        script_path: path on disk to the remix script .py file
        base_game_path: path on disk to the base game script .py file that was remixed
        remix_prompt: Infinity Arcade prompt for the remix
    """

    # Convert to variable name expected by Infinity Arcade
    mode_data = remix_prompt
    content = base_game_content

    remix_instructions = """You are an expert Python game developer. You will be given an existing pygame game and a modification request. Your task is to modify the existing game according to the user's request while keeping it fully functional.

    Rules:
    1. Use ONLY the pygame library - no external images, sounds, or files
    2. Keep the core game mechanics intact unless specifically asked to change them
    3. Make the requested modifications while ensuring the game remains playable
    4. Maintain proper pygame event handling and game loop
    5. Add comments explaining the changes you made
    6. Make sure the game window closes properly when the user clicks the X button
    7. Use reasonable colors and make the game visually appealing with pygame primitives

    Output format:
        First, a one-sentence explanation of the modification in the context of the game, starting with a phrase like "I will modify the game to...".
        Then, generate ONLY the complete modified Python code wrapped in a markdown code block using triple backticks (```python)."""

    remix_input = f"""Here is the existing game code:

    ```python
    {content}
    ```

    Please modify this game according to this request: {mode_data}

    Provide the complete modified game code."""

    return {
        "instruction": remix_instructions,
        "input": remix_input,
        "output": script_content
    }


def route_script_to_formatter(script_path: Path):
    """
    Route a script file to the appropriate formatter based on its content.
    
    Args:
        script_path: Path to the script file to process
        
    Returns:
        Dict containing the formatted instruction data
    """
    # Read the script content
    script_content = script_path.read_text(encoding='utf-8')
    
    # Check if it's a remix game by looking for SOURCE and REMIX comments
    lines = script_content.splitlines()
    
    if len(lines) >= 2 and lines[0].startswith("# SOURCE:") and lines[1].startswith("# REMIX:"):
        # This is a remix game
        source_filename = lines[0].replace("# SOURCE:", "").strip()
        remix_prompt = lines[1].replace("# REMIX:", "").strip()
        
        # Strip the first 3 lines (SOURCE comment, REMIX comment, and empty line)
        stripped_content = '\n'.join(lines[3:])
        
        # Find the base game file in the same directory
        base_game_path = script_path.parent / source_filename
        
        if not base_game_path.exists():
            raise FileNotFoundError(f"Base game file not found: {base_game_path}")
        
        # Read the base game content
        base_game_content = base_game_path.read_text(encoding='utf-8')
        
        return format_remix_game(stripped_content, base_game_content, remix_prompt)
    else:
        # This is a create game
        create_prompt = script_path.stem.replace("_", " ")
        return format_create_game(script_content, create_prompt)


def generate_dataset_json(data_dir: Path = None, output_file: Path = None):
    """
    Generate a JSON dataset from all pygame scripts in the data directory.
    
    Args:
        data_dir: Path to the data directory (defaults to ../data relative to script)
        output_file: Path for the output JSON file (defaults to dataset.json in current dir)
    
    Returns:
        List of formatted instruction data dictionaries
    """
    if data_dir is None:
        # Default to data directory relative to this script
        script_dir = Path(__file__).parent
        data_dir = script_dir.parent / "data"
    
    if output_file is None:
        # Create output directory if it doesn't exist
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "dataset.json"
    
    dataset = []
    
    # Iterate through all subdirectories in data/
    for game_dir in data_dir.iterdir():
        if game_dir.is_dir():
            print(f"Processing {game_dir.name}...")
            
            # Find all .py files in this game directory
            for script_file in game_dir.glob("*.py"):
                try:
                    print(f"  Processing {script_file.name}...")
                    formatted_data = route_script_to_formatter(script_file)
                    dataset.append(formatted_data)
                except Exception as e:
                    print(f"  Error processing {script_file}: {e}")
                    continue
    
    # Write the dataset to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"\nDataset generated with {len(dataset)} entries")
    print(f"Output saved to: {output_file.absolute()}")
    
    return dataset


if __name__ == "__main__":
    generate_dataset_json()