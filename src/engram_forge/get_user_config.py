import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent

def get_name() -> str:
    with open(os.path.join(PROJECT_DIR, "config/my_name.txt"), "r", encoding="utf-8") as f:
        return f.read().strip()


def get_base_prompt() -> str:
    with open(os.path.join(PROJECT_DIR, "config/base_system_prompt.txt"), "r", encoding="utf-8") as f:
        return f.read().strip()


def get_chat_prompt() -> str:
    with open(os.path.join(PROJECT_DIR, "config/chat_system_prompt.txt"), "r", encoding="utf-8") as f:
        return f.read().strip()

def get_prompt_for_chatting() -> str:
    return get_base_prompt() + "\n\n" + get_chat_prompt()
