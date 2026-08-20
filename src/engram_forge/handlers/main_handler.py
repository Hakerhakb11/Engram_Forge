from engram_forge.handlers.ui_helpers import check_os_if_linux, clear_screen, pause


def main_handler():
    while True:
        clear_screen()
        print("\nWelcome to Engram Forge!"
              "\nWhat you want to do?"
              "\n1. Start"
              "\n2. Data management (chat import and show chats)"
              "\n3. Change chat prompt (facts about you)"
              "\n0. Exit"
              )

        choice = input(": ")
        match choice:
            case "1":
                if check_os_if_linux():
                    from engram_forge.handlers.train_handler import train_handler
                    train_handler()

            case "2":
                from engram_forge.handlers.chats_handler import chats_handler
                clear_screen()
                chats_handler()
                pause()

            case "3":
                from engram_forge.handlers.set_prompt_handler import (
                    set_chat_prompt,
                )
                set_chat_prompt()
                pause()

            case "0":
                print("\nExiting...")
                break

            case _:
                continue
