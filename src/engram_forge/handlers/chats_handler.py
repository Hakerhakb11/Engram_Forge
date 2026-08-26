import shutil
from pathlib import Path

from engram_forge.handlers.ui_helpers import clear_screen, pause

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent.parent


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
    print("In native Linux, you can drag and drop your chat file (.json or .txt) directly into this window."
          "\nor paste full path to the file."
          "\nIn WSL linux only the option of manually entering the path."
          "\nHowever, you can always move the chats yourself to the `chats/` folder in the project root.")

    file_input = input("Enter path to file: ").strip()

    if not file_input:
        print("[ERROR] Path cannot be empty.")
        pause()
        return

    file_input = file_input.strip('"').strip("'")

    source_path = Path(file_input).expanduser()

    if not source_path.exists() or not source_path.is_file():
        print(f"[ERROR] File not found or it's not a file: {source_path}")
        pause()
        return

    if source_path.suffix not in [".json", ".txt"]:
        print(
            f"[ERROR] Unsupported format '{source_path.suffix}'. Only .json (Telegram) and .txt (WhatsApp) are allowed.")
        pause()
        return

    chats_dir = Path(PROJECT_DIR, "chats")
    chats_dir.mkdir(parents=True, exist_ok=True)

    target_path = chats_dir / source_path.name

    if target_path.exists():
        print(
            f"File '{source_path.name}' already exists in chats/.")
        pause()
        return

    try:
        shutil.copy2(source_path, target_path)
        print(
            f"\nSuccessfully imported: {target_path.name} -> saved to {chats_dir}/")
    except Exception as e:  # noqa: BLE001
        print(f"\n[ERROR] Failed to copy file: {e}")

    pause()


def show_chats():
    print("\nImported chats:")
    chats_dir = Path(PROJECT_DIR, "chats")
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
