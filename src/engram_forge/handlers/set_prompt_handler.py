from engram_forge.handlers.main_handler import clear_screen
from engram_forge.utils.get_user_config import (
    get_base_prompt,
    get_chat_prompt,
    get_name,
)


def get_multiline_input() -> str:
    print("Put your text. To save type 'END' in new line. (Press Enter to skip)")

    lines = []
    while True:
        line = input()

        if not lines and not line:
            return ""

        if line.strip() == "END":
            break

        lines.append(line)

    return "\n".join(lines).strip()


def set_name_base_prompt_handler():
    my_name = get_name()
    system_tmpl = get_base_prompt()

    clear_screen()
    default_name = input(f"Now your name: {my_name}\n"
                         "Enter default name: ").strip()
    if default_name:
        with open("config/my_name.txt", "w", encoding="utf-8") as f:
            f.write(default_name)

    clear_screen()
    print(f"Now your prompt:\n\n{'-'*20}\n{system_tmpl}\n{'-'*20}\n")
    default_prompt = get_multiline_input()
    if default_prompt:
        with open("config/base_system_prompt.txt", "w", encoding="utf-8") as f:
            f.write(default_prompt)


def set_chat_prompt():
    facts_of_me = get_chat_prompt()

    clear_screen()
    print(f"Now facts about you:\n\n{'-'*20}\n{facts_of_me}\n{'-'*20}\n")
    facts_of_me = get_multiline_input()
    if facts_of_me:
        with open("config/chat_system_prompt.txt", "w", encoding="utf-8") as f:
            f.write(facts_of_me)
