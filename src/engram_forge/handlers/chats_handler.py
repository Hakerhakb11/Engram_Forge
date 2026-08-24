import shutil
from pathlib import Path

from engram_forge.handlers.ui_helpers import clear_screen, pause


def chats_handler():
    while True:
        clear_screen()
        print("\nData management"
              "\nWhat you want to do?"
              "\n1. Import Telegram chats - (result.json) or WhatsApp chat - (*.txt)"
              "\n2. Show imported chats"
              "\n0. Exit"
              )

        choice = input(": ")
        match choice:
            case "1":
                import_handler()

            case "2":
                show_chats()

            case "0":
                return

            case _:
                continue


def import_handler():
    print("You can drag and drop your chat file (.json or .txt) directly into this window."
          "or paste full path to the file.")

    file_input = input("Enter path to file: ").strip()

    if not file_input:
        print("[ERROR] Path cannot be empty.")
        pause()
        return

    file_input = file_input.strip('"').strip("'")

    source_path = Path(file_input)

    if not source_path.exists() or not source_path.is_file():
        print(f"[ERROR] File not found or it's not a file: {source_path}")
        pause()
        return

    if source_path.suffix not in [".json", ".txt"]:
        print(
            f"[ERROR] Unsupported format '{source_path.suffix}'. Only .json (Telegram) and .txt (WhatsApp) are allowed.")
        pause()
        return

    chats_dir = Path("chats")
    chats_dir.mkdir(parents=True, exist_ok=True)

    target_path = chats_dir / source_path.name

    if target_path.exists():
        print(
        pause()

    try:
        shutil.copy2(source_path, target_path)
        print(
            f"\nSuccessfully imported: {target_path.name} -> saved to {chats_dir}/")
    except Exception as e:  # noqa: BLE001
        print(f"\n[ERROR] Failed to copy file: {e}")

    pause()


def show_chats():
    print("\nImported chats:")
    chats_dir = Path("chats")
    if not chats_dir.exists():
        print(f"{chats_dir} directory not found. Creating...")
        chats_dir.mkdir(parents=True, exist_ok=True)
        print(f"{chats_dir} directory created.")
        print("Pleace import some chat files.")
        pause()
        return

    for filepath in chats_dir.iterdir():
        if not filepath.is_file():
            print(f"Skipping {filepath.name}: Not a file.")
            continue

        if filepath.suffix == ".json":
            print(f"- {filepath.name} (Telegram .json)")
        elif filepath.suffix == ".txt":
            print(f"- {filepath.name} (WhatsApp .txt)")

    pause()
