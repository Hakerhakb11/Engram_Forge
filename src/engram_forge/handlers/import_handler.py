import shutil
from pathlib import Path


def import_handler():
    print("\n--- Import Chat File ---")
    print("You can drag and drop your chat file (.json or .txt) directly into this window." \
    "or paste full path to the file.")

    file_input = input("Enter path to file: ").strip()

    if not file_input:
        print("[ERROR] Path cannot be empty.")
        return

    file_input = file_input.strip('"').strip("'")

    source_path = Path(file_input)

    if not source_path.exists() or not source_path.is_file():
        print(f"[ERROR] File not found or it's not a file: {source_path}")
        return

    if source_path.suffix not in [".json", ".txt"]:
        print(
            f"[ERROR] Unsupported format '{source_path.suffix}'. Only .json (Telegram) and .txt (WhatsApp) are allowed.")
        return

    chats_dir = Path("chats")
    chats_dir.mkdir(parents=True, exist_ok=True)

    target_path = chats_dir / source_path.name

    if target_path.exists():
        print(
            f"File '{source_path.name}' already exists in chats/.").strip().lower()

    try:
        shutil.copy2(source_path, target_path)
        print(
            f"\nSuccessfully imported: {target_path.name} -> saved to {chats_dir}/")
    except Exception as e:  # noqa: BLE001
        print(f"\n[ERROR] Failed to copy file: {e}")
