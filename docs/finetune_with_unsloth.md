To install `unsloth` on a Strix Halo Windows PC:

```
python -m pip install --index-url https://rocm.nightlies.amd.com/v2/gfx1151/ --pre torch torchaudio torchvision

pip install --no-deps unsloth==2025.9.11

pip install "transformers==4.56.2" "accelerate==1.10.1" "datasets==4.1.1" "peft==0.17.1" "trl==0.23.0" "tqdm" "psutil" "huggingface_hub==0.35.3" "safetensors>=0.4.3" "sentencepiece>=0.2.0" "unsloth_zoo==2025.9.14" "tyro" "hf_transfer" "protobuf" "diffusers"
```