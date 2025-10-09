"""
This script downloads a Fireworks AI adapter, merges it with the base model,
converts to GGUF format, and uploads to Hugging Face.

setup:
    Follow llamacpp setup instructions in docs/togetherai.md
    pip install --upgrade huggingface_hub transformers torch peft
    Download and sign in: https://storage.googleapis.com/fireworks-public/firectl/stable/firectl.exe

Usage:
    python merge_and_upload_adapter.py <adapter_name> <output_directory> [--production PRODUCTION_NAME]

Examples:
    # Standard usage with auto-generated names
    python merge_and_upload_adapter.py my-lora-adapter ./models

    # Production usage with custom names
    python merge_and_upload_adapter.py my-lora-adapter ./models --production Playable1
    
    This creates:
    - GGUF repo: playable/Playable1-GGUF with file Playable1-q4_k_m.gguf
    - SafeTensors repo: playable/Playable1 with files Playable1-00001-of-00004.safetensors, etc.
"""

# cspell: disable

import argparse
import subprocess
import sys
from pathlib import Path


def get_model_name(adapter_name, suffix=""):
    """Generate standardized model name based on adapter name and optional suffix.

    Args:
        adapter_name: Name of the adapter
        suffix: Optional suffix like 'f16', 'q4_k_m', 'GGUF', etc.

    Returns:
        Formatted model name string
    """
    base_name = f"Qwen2.5-Coder-7B-Instruct-{adapter_name}"
    if suffix:
        return f"{base_name}-{suffix}"
    return base_name


def run_command(cmd, description, cwd=None):
    """Run a shell command and handle errors."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)

    if result.returncode != 0:
        print(f"Error: {description} failed")
        if result.stderr:
            print(f"Error output: {result.stderr}")
        sys.exit(1)

    return result


def download_adapter(adapter_name, output_dir):
    """Download adapter from Fireworks AI using firectl."""
    script_dir = Path(__file__).parent
    firectl_path = script_dir / "firectl.exe"

    if not firectl_path.exists():
        print(f"Error: firectl.exe not found at {firectl_path}")
        sys.exit(1)

    adapter_path = output_dir / adapter_name

    run_command(
        [
            str(firectl_path),
            "download",
            "model",
            adapter_name,
            str(adapter_path),
        ],
        f"Downloading adapter '{adapter_name}' from Fireworks AI",
    )

    # firectl creates nested directories, find the actual checkpoint
    # Look for adapter_config.json recursively
    checkpoint_dirs = list(adapter_path.rglob("adapter_config.json"))

    if not checkpoint_dirs:
        print(f"Error: Could not find adapter_config.json in {adapter_path}")
        print(f"Directory structure:")
        for item in adapter_path.rglob("*"):
            if item.is_file():
                print(f"  {item.relative_to(adapter_path)}")
        sys.exit(1)

    # Use the directory containing adapter_config.json
    actual_adapter_path = checkpoint_dirs[0].parent
    print(f"Found adapter at: {actual_adapter_path}")

    return actual_adapter_path


def merge_adapter_with_base(
    adapter_path, output_dir, base_model="Qwen/Qwen2.5-Coder-7B-Instruct"
):
    """Merge the adapter with the base model."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    from peft import PeftModel
    import warnings

    # Suppress expected warnings during adapter merging
    warnings.filterwarnings("ignore", message=".*copying from a non-meta parameter.*")

    print(f"\n{'='*60}")
    print(f"Loading base model: {base_model}")
    print(f"{'='*60}")

    # Load base model - use low_cpu_mem_usage instead of device_map to avoid offload issues
    base_model_obj = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
        trust_remote_code=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)

    print(f"\n{'='*60}")
    print(f"Loading and merging adapter from: {adapter_path}")
    print(f"{'='*60}")

    # Load adapter and merge
    model = PeftModel.from_pretrained(base_model_obj, str(adapter_path))
    model = model.merge_and_unload()

    # Move to CPU for saving (to avoid CUDA OOM issues)
    model = model.cpu()

    # Save merged model
    merged_path = output_dir / "merged_model"
    merged_path.mkdir(exist_ok=True, parents=True)

    print(f"\n{'='*60}")
    print(f"Saving merged model to: {merged_path}")
    print(f"{'='*60}")

    model.save_pretrained(str(merged_path))
    tokenizer.save_pretrained(str(merged_path))

    return merged_path


def convert_to_gguf(merged_model_path, output_dir, adapter_name, production_name=None):
    """Convert merged model to GGUF format."""
    # Path to llama.cpp (relative to workspace)
    script_dir = Path(__file__).parent
    llamacpp_path = script_dir / ".." / ".." / ".." / "llama.cpp"
    llamacpp_path = llamacpp_path.resolve()

    if not llamacpp_path.exists():
        print(f"Error: llama.cpp not found at {llamacpp_path}")
        sys.exit(1)

    convert_script = llamacpp_path / "convert_hf_to_gguf.py"
    if not convert_script.exists():
        # Try older naming
        convert_script = llamacpp_path / "convert.py"

    if not convert_script.exists():
        print(f"Error: convert script not found in {llamacpp_path}")
        sys.exit(1)

    # Convert to GGUF F16 first
    if production_name:
        gguf_f16_path = output_dir / f"{production_name}-f16.gguf"
    else:
        gguf_f16_path = output_dir / f"{get_model_name(adapter_name, 'f16')}.gguf"

    run_command(
        [
            "python",
            str(convert_script),
            str(merged_model_path),
            "--outfile",
            str(gguf_f16_path),
            "--outtype",
            "f16",
        ],
        "Converting merged model to GGUF F16 format",
    )

    # Quantize to q4_k_m
    quantize_bin = llamacpp_path / "build" / "bin" / "llama-quantize.exe"
    if not quantize_bin.exists():
        # Try Release folder
        quantize_bin = (
            llamacpp_path / "build" / "bin" / "Release" / "llama-quantize.exe"
        )
    if not quantize_bin.exists():
        # Try without .exe (for Unix-like systems)
        quantize_bin = llamacpp_path / "build" / "bin" / "llama-quantize"

    if not quantize_bin.exists():
        print(f"Error: llama-quantize not found at {quantize_bin}")
        sys.exit(1)

    if production_name:
        gguf_q4km_path = output_dir / f"{production_name}-q4_k_m.gguf"
    else:
        gguf_q4km_path = output_dir / f"{get_model_name(adapter_name, 'q4_k_m')}.gguf"

    run_command(
        [str(quantize_bin), str(gguf_f16_path), str(gguf_q4km_path), "q4_k_m"],
        "Quantizing to q4_k_m format",
    )

    return gguf_q4km_path


def upload_to_huggingface(gguf_path, adapter_name, merged_model_path=None, production_name=None):
    """Upload the GGUF model to Hugging Face."""
    from huggingface_hub import HfApi, create_repo
    import re

    # Determine repo name based on production_name
    if production_name:
        repo_name = f"{production_name}-GGUF"
    else:
        repo_name = get_model_name(adapter_name, "GGUF")
    
    repo_id = f"playable/{repo_name}"

    print(f"\n{'='*60}")
    print(f"Creating/uploading to Hugging Face repository: {repo_id}")
    print(f"{'='*60}")

    api = HfApi()

    # Create repo if it doesn't exist
    try:
        create_repo(repo_id, exist_ok=True, repo_type="model")
        print(f"Repository created/verified: {repo_id}")
    except Exception as e:
        print(f"Error creating repository: {e}")
        sys.exit(1)

    # Upload GGUF file
    try:
        api.upload_file(
            path_or_fileobj=str(gguf_path),
            path_in_repo=gguf_path.name,
            repo_id=repo_id,
            repo_type="model",
        )
        print(f"Successfully uploaded {gguf_path.name} to {repo_id}")

        # Create and upload README
        readme_content = f"""---
license: apache-2.0
base_model: Qwen/Qwen2.5-Coder-7B-Instruct
tags:
- gguf
- quantized
- q4_k_m
---

# {repo_name}

This is a GGUF quantized version (q4_k_m) of Qwen/Qwen2.5-Coder-7B-Instruct fine-tuned with the '{adapter_name}' adapter.

## Model Details

- **Base Model:** Qwen/Qwen2.5-Coder-7B-Instruct
- **Adapter:** {adapter_name}
- **Quantization:** q4_k_m
- **Format:** GGUF

## Usage

This model can be used with llama.cpp or any compatible inference engine that supports GGUF format.

```bash
# Example with llama.cpp
./llama-cli -m {gguf_path.name} -p "Your prompt here"
```

## Files

- `{gguf_path.name}` - Quantized model in GGUF format (q4_k_m)
"""

        readme_path = gguf_path.parent / "README.md"
        readme_path.write_text(readme_content)

        api.upload_file(
            path_or_fileobj=str(readme_path),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="model",
        )
        print(f"Successfully uploaded README.md to {repo_id}")

    except Exception as e:
        print(f"Error uploading to Hugging Face: {e}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"✓ Upload complete!")
    print(f"Model available at: https://huggingface.co/{repo_id}")
    print(f"{'='*60}")

    # If production_name is set, also upload safetensors to a separate repo
    if production_name and merged_model_path:
        upload_safetensors_to_huggingface(merged_model_path, production_name, adapter_name, api)


def upload_safetensors_to_huggingface(merged_model_path, production_name, adapter_name, api):
    """Upload safetensors to a separate Hugging Face repository."""
    from huggingface_hub import create_repo

    repo_id = f"playable/{production_name}"

    print(f"\n{'='*60}")
    print(f"Creating/uploading safetensors to Hugging Face repository: {repo_id}")
    print(f"{'='*60}")

    # Create repo if it doesn't exist
    try:
        create_repo(repo_id, exist_ok=True, repo_type="model")
        print(f"Repository created/verified: {repo_id}")
    except Exception as e:
        print(f"Error creating repository: {e}")
        sys.exit(1)

    # Find all safetensors files in the merged model directory
    merged_path = Path(merged_model_path)
    safetensors_files = list(merged_path.glob("*.safetensors"))
    
    if not safetensors_files:
        print(f"Warning: No safetensors files found in {merged_path}")
        return

    # Rename and upload safetensors files
    import re
    for safetensor_file in safetensors_files:
        # Match pattern like "model-00001-of-00004.safetensors"
        match = re.match(r'model-(\d+-of-\d+)\.safetensors', safetensor_file.name)
        if match:
            new_name = f"{production_name}-{match.group(1)}.safetensors"
        else:
            # Handle single file case: "model.safetensors"
            if safetensor_file.name == "model.safetensors":
                new_name = f"{production_name}.safetensors"
            else:
                new_name = safetensor_file.name
        
        try:
            api.upload_file(
                path_or_fileobj=str(safetensor_file),
                path_in_repo=new_name,
                repo_id=repo_id,
                repo_type="model",
            )
            print(f"Successfully uploaded {new_name} to {repo_id}")
        except Exception as e:
            print(f"Error uploading {safetensor_file.name}: {e}")
            sys.exit(1)

    # Upload other necessary files (config.json, tokenizer files, etc.)
    other_files = [
        "config.json",
        "generation_config.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "merges.txt",
        "vocab.json",
        "special_tokens_map.json",
    ]
    
    for filename in other_files:
        file_path = merged_path / filename
        if file_path.exists():
            try:
                api.upload_file(
                    path_or_fileobj=str(file_path),
                    path_in_repo=filename,
                    repo_id=repo_id,
                    repo_type="model",
                )
                print(f"Successfully uploaded {filename} to {repo_id}")
            except Exception as e:
                print(f"Warning: Error uploading {filename}: {e}")

    # Create and upload README for safetensors repo
    readme_content = f"""---
license: apache-2.0
base_model: Qwen/Qwen2.5-Coder-7B-Instruct
tags:
- safetensors
- text-generation
---

# {production_name}

This is a fine-tuned version of Qwen/Qwen2.5-Coder-7B-Instruct using the '{adapter_name}' adapter.

## Model Details

- **Base Model:** Qwen/Qwen2.5-Coder-7B-Instruct
- **Adapter:** {adapter_name}
- **Format:** SafeTensors

## Usage

This model can be used with transformers library:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("playable/{production_name}")
tokenizer = AutoTokenizer.from_pretrained("playable/{production_name}")

inputs = tokenizer("Your prompt here", return_tensors="pt")
outputs = model.generate(**inputs)
print(tokenizer.decode(outputs[0]))
```
"""

    readme_path = merged_path / "README_safetensors.md"
    readme_path.write_text(readme_content)

    try:
        api.upload_file(
            path_or_fileobj=str(readme_path),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="model",
        )
        print(f"Successfully uploaded README.md to {repo_id}")
    except Exception as e:
        print(f"Error uploading README: {e}")

    print(f"\n{'='*60}")
    print(f"✓ SafeTensors upload complete!")
    print(f"Model available at: https://huggingface.co/{repo_id}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description="Download Fireworks AI adapter, merge with base model, convert to GGUF, and upload to Hugging Face"
    )
    parser.add_argument("adapter_name", help="Name of the adapter on Fireworks AI")
    parser.add_argument(
        "output_directory", help="Directory to store intermediate files and output"
    )
    parser.add_argument(
        "--production",
        dest="production_name",
        help="Production model name. When set, creates simplified naming: PRODUCTION_NAME-GGUF repo with PRODUCTION_NAME-q4_k_m.gguf file, and PRODUCTION_NAME repo with safetensors files.",
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_directory)
    output_dir.mkdir(exist_ok=True, parents=True)

    print(f"\n{'='*60}")
    print(f"FIREWORKS AI ADAPTER TO GGUF PIPELINE")
    print(f"{'='*60}")
    print(f"Adapter Name: {args.adapter_name}")
    print(f"Output Directory: {output_dir.absolute()}")
    if args.production_name:
        print(f"Production Name: {args.production_name}")
    print(f"{'='*60}")

    # Step 1: Download adapter
    adapter_path = download_adapter(args.adapter_name, output_dir)

    # Step 2: Merge adapter with base model
    merged_model_path = merge_adapter_with_base(adapter_path, output_dir)

    # Step 3: Convert to GGUF and quantize
    gguf_path = convert_to_gguf(merged_model_path, output_dir, args.adapter_name, args.production_name)

    # Step 4: Upload to Hugging Face
    upload_to_huggingface(gguf_path, args.adapter_name, merged_model_path, args.production_name)

    print(f"\n{'='*60}")
    print(f"✓ ALL STEPS COMPLETED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"Final GGUF model: {gguf_path}")
    if args.production_name:
        print(f"GGUF repo: playable/{args.production_name}-GGUF")
        print(f"SafeTensors repo: playable/{args.production_name}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
