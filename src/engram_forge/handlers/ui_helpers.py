import os
import platform


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def pause():
    input("\nPress Enter to return...")


def check_os_if_linux() -> bool:
    current_os = platform.system()

    if current_os != "Linux":
        print("\n[ERROR] Train are impossible!")
        print(f"Your oS: {current_os}.")
        print("Library Unsloth and CUDA Settings requires Linux")
        print("Please, run Engram Forge from WSL for training.")
        return False

    return True
