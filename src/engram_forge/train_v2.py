# train_v2.py — QLoRA fine-tuning of Qwen3.5-4B on train_v2.jsonl.
# Run WITH WSL Linux with train.sh.
#
# Checkpoint stoage ~/tgstyle/out
# Final LoRA copy in project folder (lora_adapters/{lora_file}).

import os  # noqa: I001
import argparse
from pathlib import Path

from unsloth import FastModel  # unsloth import must be before transformers
from datasets import load_dataset
from transformers import EarlyStoppingCallback
from transformers.trainer_utils import get_last_checkpoint
from trl import SFTConfig, SFTTrainer
from unsloth.chat_templates import train_on_responses_only

MAX_SEQ_LEN = 1024
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
TRAIN_FILE: Path = PROJECT_DIR / "train_data/train_v2.jsonl"
VAL_FILE: Path = PROJECT_DIR / "train_data/val_v2.jsonl"

OUT_DIR = os.path.expanduser("~/tgstyle/out")

SAVE_STEPS = 50  # checkpoint ~every 30 min

if not TRAIN_FILE.exists() or not VAL_FILE.exists():
    raise FileNotFoundError(f"File {TRAIN_FILE} doesn't found! Build Dataset please.")
if TRAIN_FILE.stat().st_size == 0 or VAL_FILE.stat().st_size == 0:
    raise ValueError(f"File {TRAIN_FILE} is empty you need to inport chat before Build Dataset.")

def run(model_name, epochs_num, lora_name):
    LORA_DIR = os.path.join(PROJECT_DIR, "lora_adapters", lora_name)
    model, tokenizer = FastModel.from_pretrained(
        model_name=model_name,
        max_seq_length=MAX_SEQ_LEN,
        load_in_4bit=True,
    )

    model = FastModel.get_peft_model(
        model,
        r=16,
        lora_alpha=32,
        lora_dropout=0,
        bias="none",
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    dataset = load_dataset(
        "json", data_files={"train": str(TRAIN_FILE), "validation": str(VAL_FILE)}
    )

    def to_text(example):
        return {
            "text": tokenizer.apply_chat_template(
                example["messages"], tokenize=False, add_generation_prompt=False
            )
        }

    dataset = dataset.map(
        to_text, remove_columns=dataset["train"].column_names)

    print("=== Example rendered text (template check) ===")
    print(dataset["train"][0]["text"][:1500])
    print("========================================================")

    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        args=SFTConfig(
            output_dir=OUT_DIR,
            dataset_text_field="text",
            max_seq_length=MAX_SEQ_LEN,
            per_device_train_batch_size=1,
            per_device_eval_batch_size=1,
            gradient_accumulation_steps=32,
            learning_rate=2e-4,
            num_train_epochs=epochs_num,
            warmup_ratio=0.03,
            lr_scheduler_type="cosine",
            optim="adamw_8bit",
            bf16=True,
            logging_steps=5,
            eval_strategy="steps",
            eval_steps=SAVE_STEPS,
            save_strategy="steps",
            save_steps=SAVE_STEPS,
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            disable_tqdm=True,  # clean log: lines with loss instead of progress bar
            report_to="none",
            seed=42,
        ),
        callbacks=[EarlyStoppingCallback(early_stopping_patience=4)],
    )

    # Loss calculated only on my replies (between <|im_start|>assistant and <|im_end|>)
    trainer = train_on_responses_only(
        trainer,
        instruction_part="<|im_start|>user\n",
        response_part="<|im_start|>assistant\n",
    )

    last_ckpt = get_last_checkpoint(
        OUT_DIR) if os.path.isdir(OUT_DIR) else None
    if last_ckpt:
        print(f">>> Continue from checkpoint: {last_ckpt}")
    else:
        print(">>> RE:start from ZERO")

    trainer.train(resume_from_checkpoint=last_ckpt)

    # Best adapter (by eval_loss) saved to the project folder
    model.save_pretrained(LORA_DIR)
    tokenizer.save_pretrained(LORA_DIR)
    print("\n\nDONE!!!! LoRA SAVE IN:", LORA_DIR)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QLoRA train model")

    parser.add_argument("--model", type=str, default="unsloth/Qwen3.5-4B",
                        help="Name model from HuggingFace")

    parser.add_argument("--epochs", type=int, default=2,
                        help="Epochs count")

    parser.add_argument("--lora_name", type=str, default="lora_v2",
                        help="Name lora file")

    args = parser.parse_args()
    run(model_name=args.model, epochs_num=args.epochs, lora_name=args.lora_name)
