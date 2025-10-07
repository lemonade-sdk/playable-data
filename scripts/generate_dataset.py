"""
This script takes the pygame scripts from the data directory and formats them
into a JSONL file compatible with Together.ai fine-tuning.

usage: `python generate_dataset.py`
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

    # Format the output as a markdown code block
    formatted_output = f"```python\n{script_content}\n```"

    return {
        "messages": [
            {"role": "system", "content": create_instructions},
            {"role": "user", "content": create_input},
            {"role": "assistant", "content": formatted_output},
        ]
    }


def format_remix_game(script_content: str, base_game_content: str, remix_prompt: str):
    """
    Format a remix script into instruct data.

    Args:
        script_content: The content of the remix script file
        base_game_content: The content of the base game script that was remixed
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

    # Format the output as a markdown code block
    formatted_output = f"```python\n{script_content}\n```"

    return {
        "messages": [
            {"role": "system", "content": remix_instructions},
            {"role": "user", "content": remix_input},
            {"role": "assistant", "content": formatted_output},
        ]
    }


def format_bug_fix_game(bug_content: str, fixed_content: str, error_trace: str):
    """
    Format a bug/fix pair into instruct data.

    Args:
        bug_content: The content of the buggy script file (with CREATE and ERROR comments stripped)
        fixed_content: The content of the fixed script file
        error_trace: The error stack trace from the ERROR comments
    """

    bug_fix_instructions = """You are a Python expert debugging a pygame script that has an error. Generate ONLY the fixed Python code wrapped in a markdown code block using triple backticks (```python). Do not include any explanations outside the code block."""

    bug_fix_input = f"""Error:
{error_trace}

Script with error:
```python
{bug_content}
```

Please fix the bug and provide the corrected code."""

    # Format the output as a markdown code block
    formatted_output = f"```python\n{fixed_content}\n```"

    return {
        "messages": [
            {"role": "system", "content": bug_fix_instructions},
            {"role": "user", "content": bug_fix_input},
            {"role": "assistant", "content": formatted_output},
        ]
    }


def route_script_to_formatter(script_path: Path):
    """
    Route a script file to the appropriate formatter based on its content.

    Args:
        script_path: Path to the script file to process

    Returns:
        Tuple of (formatted instruction data dict, game type string, line count)
        where game_type is either "base", "remix", or "bug_fix"
        Returns None if this is a "_fixed.py" file (will be processed with its bug pair)
    """
    # Skip _fixed.py files as they're processed with their bug counterparts
    if script_path.stem.endswith("_fixed"):
        return None
    
    # Check if this is a bug file
    if script_path.stem.endswith("_bug"):
        # Find the corresponding fixed file
        fixed_filename = script_path.stem.replace("_bug", "_fixed") + ".py"
        fixed_path = script_path.parent / fixed_filename
        
        if not fixed_path.exists():
            raise FileNotFoundError(f"Fixed file not found: {fixed_path}")
        
        # Read both files
        bug_content = script_path.read_text(encoding="utf-8")
        fixed_content = fixed_path.read_text(encoding="utf-8")
        
        # Extract ERROR comments and strip them along with CREATE comment from bug file
        bug_lines = bug_content.splitlines()
        error_lines = []
        start_index = 0
        
        for i, line in enumerate(bug_lines):
            if line.startswith("# ERROR:"):
                error_lines.append(line.replace("# ERROR: ", ""))
            elif line.startswith("# CREATE:"):
                continue
            elif line.strip() == "":
                # Skip empty lines after comments
                if i < 10:  # Only skip early empty lines
                    continue
                else:
                    start_index = i + 1
                    break
            else:
                start_index = i
                break
        
        error_trace = "\n".join(error_lines)
        stripped_bug_content = "\n".join(bug_lines[start_index:])
        
        # Strip the CREATE comment from fixed file if present
        fixed_lines = fixed_content.splitlines()
        if len(fixed_lines) >= 1 and fixed_lines[0].startswith("# CREATE:"):
            stripped_fixed_content = "\n".join(fixed_lines[2:])
        else:
            stripped_fixed_content = fixed_content
        
        # Count lines in the fixed version
        line_count = len(
            [line for line in stripped_fixed_content.splitlines() if line.strip()]
        )
        
        return (
            format_bug_fix_game(stripped_bug_content, stripped_fixed_content, error_trace),
            "bug_fix",
            line_count,
        )
    
    # Read the script content
    script_content = script_path.read_text(encoding="utf-8")

    # Check if it's a remix game by looking for SOURCE and REMIX comments
    lines = script_content.splitlines()

    if (
        len(lines) >= 2
        and lines[0].startswith("# SOURCE:")
        and lines[1].startswith("# REMIX:")
    ):
        # This is a remix game
        source_filename = lines[0].replace("# SOURCE:", "").strip()
        remix_prompt = lines[1].replace("# REMIX:", "").strip()

        # Strip the first 3 lines (SOURCE comment, REMIX comment, and empty line)
        stripped_content = "\n".join(lines[3:])
        line_count = len(
            [line for line in stripped_content.splitlines() if line.strip()]
        )

        # Find the base game file in the same directory
        base_game_path = script_path.parent / source_filename

        if not base_game_path.exists():
            raise FileNotFoundError(f"Base game file not found: {base_game_path}")

        # Read the base game content
        base_game_content = base_game_path.read_text(encoding="utf-8")

        return (
            format_remix_game(stripped_content, base_game_content, remix_prompt),
            "remix",
            line_count,
        )
    elif len(lines) >= 1 and lines[0].startswith("# CREATE:"):
        # This is a create game with an explicit CREATE prompt
        create_prompt = lines[0].replace("# CREATE:", "").strip()

        # Strip the first 2 lines (CREATE comment and empty line)
        stripped_content = "\n".join(lines[2:])
        line_count = len(
            [line for line in stripped_content.splitlines() if line.strip()]
        )

        return format_create_game(stripped_content, create_prompt), "base", line_count
    else:
        # This is a create game without explicit CREATE comment (backward compatibility)
        create_prompt = script_path.stem.replace("_", " ")
        line_count = len([line for line in lines if line.strip()])
        return format_create_game(script_content, create_prompt), "base", line_count


def generate_dataset_json(data_dir: Path = None, output_file: Path = None):
    """
    Generate a JSONL dataset from all pygame scripts in the data directory.

    Args:
        data_dir: Path to the data directory (defaults to ../data relative to script)
        output_file: Path for the output JSONL file (defaults to dataset.jsonl in output dir)

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
        output_file = output_dir / "dataset.jsonl"

    dataset = []

    # Statistics tracking
    base_games_count = 0
    remix_games_count = 0
    bug_fix_count = 0
    base_games_lines = 0
    remix_games_lines = 0
    bug_fix_lines = 0

    # Iterate through all subdirectories in data/
    for game_dir in data_dir.iterdir():
        if game_dir.is_dir() and not game_dir.name.startswith("_"):
            print(f"Processing {game_dir.name}...")

            # Find all .py files in this game directory (base and remix games)
            for script_file in game_dir.glob("*.py"):
                try:
                    print(f"  Processing {script_file.name}...")
                    result = route_script_to_formatter(script_file)
                    
                    # Skip if None (shouldn't happen in parent dir)
                    if result is None:
                        continue
                    
                    formatted_data, game_type, line_count = result
                    dataset.append(formatted_data)

                    # Update statistics (only base/remix in parent dir)
                    if game_type == "base":
                        base_games_count += 1
                        base_games_lines += line_count
                    elif game_type == "remix":
                        remix_games_count += 1
                        remix_games_lines += line_count
                except Exception as e:
                    print(f"  Error processing {script_file}: {e}")
                    continue
            
            # Also check for a bugs subdirectory (only bug/fix pairs here)
            bugs_dir = game_dir / "bugs"
            if bugs_dir.exists() and bugs_dir.is_dir():
                print(f"  Processing bugs subdirectory...")
                for script_file in bugs_dir.glob("*.py"):
                    try:
                        print(f"    Processing {script_file.name}...")
                        result = route_script_to_formatter(script_file)
                        
                        # Skip if None (e.g., _fixed.py files)
                        if result is None:
                            print(f"    Skipping {script_file.name} (processed with bug pair)")
                            continue
                        
                        formatted_data, game_type, line_count = result
                        dataset.append(formatted_data)

                        # Update statistics (only bug_fix in bugs dir)
                        bug_fix_count += 1
                        bug_fix_lines += line_count
                    except Exception as e:
                        print(f"    Error processing {script_file}: {e}")
                        continue

    # Write the dataset to JSONL file (one JSON object per line)
    with open(output_file, "w", encoding="utf-8") as f:
        for entry in dataset:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")

    # Print statistics in a table
    total_games = base_games_count + remix_games_count + bug_fix_count
    total_lines = base_games_lines + remix_games_lines + bug_fix_lines

    print("\n" + "=" * 60)
    print("DATASET STATISTICS")
    print("=" * 60)
    print(f"{'Game Type':<20} {'Count':<15} {'Lines of Code':<20}")
    print("-" * 60)
    print(f"{'Base Games':<20} {base_games_count:<15} {base_games_lines:<20,}")
    print(f"{'Remix Games':<20} {remix_games_count:<15} {remix_games_lines:<20,}")
    print(f"{'Bug Fix Games':<20} {bug_fix_count:<15} {bug_fix_lines:<20,}")
    print("-" * 60)
    print(f"{'TOTAL':<20} {total_games:<15} {total_lines:<20,}")
    print("=" * 60)
    print(f"\nOutput saved to: {output_file.absolute()}")

    return dataset


if __name__ == "__main__":
    generate_dataset_json()
