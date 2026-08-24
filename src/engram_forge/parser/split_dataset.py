# split_dataset.py — train/val split multi-turn dataset
import json
import random
from pathlib import Path


def run(PROJECT_DIR):
    input_path:Path = PROJECT_DIR / "train_data/dataset_sanitized.jsonl"
    train_out_path:Path = PROJECT_DIR / "train_data/train_v2.jsonl"
    value_out_path:Path = PROJECT_DIR / "train_data/val_v2.jsonl"
    
    VAL_FRACTION = 0.03
    VAL_MIN = 300

    random.seed(42)

    rows = []
    print("\nSPLIT Start -----------------.")
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                obj = json.loads(line)
                msgs = obj.get("messages", [])
                has_assistant = any(
                    m.get("role") == "assistant" and m.get("content") for m in msgs)
                has_user = any(m.get("role") == "user" and m.get("content")
                               for m in msgs)
                if has_assistant and has_user:
                    rows.append(obj)

        random.shuffle(rows)

        val_n = max(VAL_MIN, int(len(rows) * VAL_FRACTION))
        val, train = rows[:val_n], rows[val_n:]

        with open(train_out_path, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(r, ensure_ascii=False) +
                         "\n" for r in train)

        with open(value_out_path, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in val)

        print("DONE.")
        print("Delete: " + input_path)
        Path(input_path).unlink(missing_ok=True)
        print("All:", len(rows))
        print("Train:", len(train))
        print("Val:", len(val))
    except FileNotFoundError:
        print(f"{input_path} file not found:")
