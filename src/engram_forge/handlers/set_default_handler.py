from engram_forge.handlers.main_handler import clear_screen
from engram_forge.utils.get_user_config import (
    get_facts,
    get_name,
    get_system_prompt,
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


def set_default_handler():
    my_name = get_name()
    system_tmpl = get_system_prompt()
    facts_of_me = get_facts()

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
        with open("config/system_prompt.txt", "w", encoding="utf-8") as f:
            f.write(default_prompt)

    clear_screen()
    print(f"Now facts about you:\n\n{'-'*20}\n{facts_of_me}\n{'-'*20}\n")
    facts_of_me = get_multiline_input()
    if facts_of_me:
        with open("config/facts_of_me.txt", "w", encoding="utf-8") as f:
            f.write(facts_of_me)

    print("\nDefault name and prompt set successfully!")
