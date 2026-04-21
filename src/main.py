# configure the logger
from config.setup import setup_logging
setup_logging()

print("application initialize...")

from colorama import Fore, Style
from cli.input import (
    initialize_new_tracking_process,
    quick_user_comparison,
    manual_file_comparison,
    configure_browser_login,
)
from common.utils import clear, pause
import asyncio
import inspect
import sys


def main():
    while True:
        clear()

        print("select which operation you want to choose:\n\n")
        print(Fore.LIGHTCYAN_EX)
        print("[1]. run a new tracking scene")
        print("[2]. compares recent users record")
        print("[3]. file selection from the various list of users records")
        print(Style.RESET_ALL)
        print("\n" + "=" * 60 + "\n")
        print(Fore.LIGHTYELLOW_EX)
        print("[x]. press and enter [x] to exit")
        print("[v]. open browser to set up (recomended for first launch)")
        print(Style.RESET_ALL)

        options = {
            "1": initialize_new_tracking_process,
            "2": quick_user_comparison,
            "3": manual_file_comparison,
            "v": configure_browser_login,
        }

        try:
            choice = input("\n\n:").lower().strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Fore.RED}Exiting...{Style.RESET_ALL}")
            break

        if choice == "x":
            break

        if choice in options:
            clear()
            func = options[choice]

            try:
                if inspect.iscoroutinefunction(func):
                    asyncio.run(func())
                else:
                    func()
            except KeyboardInterrupt:
                continue
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                pause()


if __name__ == "__main__":
    main()
