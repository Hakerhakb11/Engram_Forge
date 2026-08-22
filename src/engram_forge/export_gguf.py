# export_to_gguf.py — Script for merging base model with LoRA and exporting to .gguf
# Usage: python export_to_gguf.py --lora_name lora_v2 --quant q4_k_m

import argparse
import shutil
from pathlib import Path

from unsloth import FastModel

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent


def export_gguf(lora_name):
    LORA_DIR = PROJECT_DIR / "lora_adapters" / lora_name
    EXPORT_DIR = PROJECT_DIR / "exported_models" / lora_name
    GGUF_DIR = PROJECT_DIR / "exported_models" / f"{lora_name}_gguf"

    print(f"Loading adapter from {LORA_DIR}...")

    model, tokenizer = FastModel.from_pretrained(
        model_name=str(LORA_DIR),
        max_seq_length=1024,
        dtype=None,
        load_in_4bit=True,
    )

    print("Starting export to GGUF (q4_k_m)...")

    model.save_pretrained_gguf(
        str(EXPORT_DIR),
        tokenizer,
        quantization_method="q4_k_m"
    )

    # Cleanup: remove all temporary non-gguf files, leaving only the final .gguf file
    if GGUF_DIR.exists():
        for file_path in GGUF_DIR.glob("*mmproj.gguf"):
            file_path.unlink()
            print(f"Trash file {file_path.name} was deleted")

    if EXPORT_DIR.exists():
        shutil.rmtree(EXPORT_DIR)
        print(f"Trash folder {EXPORT_DIR.name} was deleted")

    print(f"Done! Your GGUF file is located here: {EXPORT_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export LoRA to GGUF format")

    parser.add_argument("--lora_name", type=str, required=True,
                        help="Name of the adapter folder (e.g., lora_v2)")

    args = parser.parse_args()

    export_gguf(args.lora_name)
