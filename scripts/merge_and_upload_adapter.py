"""
This script downloads a Fireworks AI adapter, merges it with the base model,
converts to GGUF format, and uploads to Hugging Face.

setup:
    pip install --upgrade huggingface_hub transformers torch peft
    Download and sign in: https://storage.googleapis.com/fireworks-public/firectl/stable/firectl.exe

Usage:
    python merge_and_upload_adapter.py <adapter_name> <output_directory>

Example:
    python merge_and_upload_adapter.py my-lora-adapter ./models
"""

# cspell: disable

import argparse
import subprocess
import sys
from pathlib import Path
import shutil


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


def convert_to_gguf(merged_model_path, output_dir):
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
    gguf_f16_path = output_dir / "model_f16.gguf"

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

    gguf_q4km_path = output_dir / "model_q4_k_m.gguf"

    run_command(
        [str(quantize_bin), str(gguf_f16_path), str(gguf_q4km_path), "q4_k_m"],
        "Quantizing to q4_k_m format",
    )

    return gguf_q4km_path


def upload_to_huggingface(gguf_path, adapter_name):
    """Upload the GGUF model to Hugging Face."""
    from huggingface_hub import HfApi, create_repo

    repo_name = f"Qwen2.5-Coder-7B-Instruct-{adapter_name}-GGUF"
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


def main():
    parser = argparse.ArgumentParser(
        description="Download Fireworks AI adapter, merge with base model, convert to GGUF, and upload to Hugging Face"
    )
    parser.add_argument("adapter_name", help="Name of the adapter on Fireworks AI")
    parser.add_argument(
        "output_directory", help="Directory to store intermediate files and output"
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
    print(f"{'='*60}")

    # Step 1: Download adapter
    adapter_path = download_adapter(args.adapter_name, output_dir)

    # Step 2: Merge adapter with base model
    merged_model_path = merge_adapter_with_base(adapter_path, output_dir)

    # Step 3: Convert to GGUF and quantize
    gguf_path = convert_to_gguf(merged_model_path, output_dir)

    # Step 4: Upload to Hugging Face
    upload_to_huggingface(gguf_path, args.adapter_name)

    print(f"\n{'='*60}")
    print(f"✓ ALL STEPS COMPLETED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"Final GGUF model: {gguf_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
