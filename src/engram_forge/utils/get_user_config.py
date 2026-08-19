def get_name() -> str:
    with open("config/my_name.txt", "r", encoding="utf-8") as f:
        return f.read().strip()


def get_system_prompt() -> str:
    with open("config/system_prompt.txt", "r", encoding="utf-8") as f:
        return f.read().strip()


def get_facts() -> str:
    with open("config/facts_of_me.txt", "r", encoding="utf-8") as f:
        return f.read().strip()

def get_system_prompt_with_facts() -> str:
    return get_system_prompt() + "\n\n" + get_facts()
