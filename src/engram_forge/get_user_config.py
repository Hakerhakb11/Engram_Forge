def get_name() -> str:
    with open("config/my_name.txt", "r", encoding="utf-8") as f:
        return f.read().strip()


def get_base_prompt() -> str:
    with open("config/base_system_prompt.txt", "r", encoding="utf-8") as f:
        return f.read().strip()


def get_chat_prompt() -> str:
    with open("config/chat_system_prompt.txt", "r", encoding="utf-8") as f:
        return f.read().strip()

def get_prompt_for_chatting() -> str:
    return get_base_prompt() + "\n\n" + get_chat_prompt()
