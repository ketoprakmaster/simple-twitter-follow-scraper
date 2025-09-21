from core.twitterDriver import TwitterDriver
from core.utils import pause, clear
from core.exceptions import NotEnoughUserRecords, FiledecodeError, UserRecordsNotExists
from core.types import MODE, ComparisonResults
from core.config import USER_RECORDS_DIR
from core.userHandling import (
    compareRecentRecords,
    compareToRecentUsersRecords,
    saveUsersRecord,
    readFromRecords,
    returnAllRecords,
    makeComparison
)

from colorama import Style, Fore
from pathlib import Path
import logging

console_log = logging.getLogger("console")


def file_selection(directory: Path, msg: str = "") -> Path:
    """
    Lists files in a given directory and allows the user to select one.
    Returns the selected file path.
    """
    files = returnAllRecords(path=directory)
    console_log.info(f"Total files: {len(files)}")

    while True:
        clear()
        print(f"{msg}\n\nUser directory: {directory}\n")
        for i, file in enumerate(files):
            print(f"{Fore.CYAN}[{i + 1}]. {file.name}{Style.RESET_ALL}")
        try:
            choice = int(input("Enter the number of the file to select: "))
            if 1 <= choice <= len(files):
                clear()
                return files[choice - 1]
        except ValueError:
            continue


def initialize_new_tracking_process():
    """
    Starts a new Twitter scraping session, saves the user records,
    and compares against previous records.
    """
    mode = ask_mode_selection()
    headless = ask_headless_mode()
    clear()

    try:
        scraper = TwitterDriver(headless=headless, mode=mode)
        scraper.initialize_driver()
        users = scraper.scrape_user_follows()
        username = scraper.username
    except Exception as e:
        console_log.error(f"Failed to initialize scraper. Check internet connection.\n{e}")
        pause()
        return
    finally:
        scraper.quit()

    results = compareToRecentUsersRecords(username, mode, users)
    if results.added or results.removed:
        saveUsersRecord(username=username,mode=mode,users_set=users)
        output_comparison_results(record=results)
    else:
        console_log.info("no users changes detected, skip saving")
        pause()


def quick_user_comparison():
    """
    Quickly compares the two most recent records of a user.
    """
    username = input("Enter username to compare: ").lower()
    mode = ask_mode_selection()

    try:
        results = compareRecentRecords(username, mode)
        output_comparison_results(results)
    except (NotEnoughUserRecords, UserRecordsNotExists, FiledecodeError):
        pause()


def manual_file_comparison():
    """
    Manually select two record files to compare for a given user.
    """
    username = input("Enter username to compare records: ").lower()
    mode = ask_mode_selection()

    user_path = USER_RECORDS_DIR / username / mode
    if not user_path.exists():
        console_log.error(f"No user records found at: {user_path}")
        pause()
        return

    try:
        past_path = file_selection(user_path, msg="Select the *past* record file")
        future_path = file_selection(user_path, msg="Select the *future* record file")
        past_users = readFromRecords(past_path)
        future_users = readFromRecords(future_path)
    except (UserRecordsNotExists, FileNotFoundError):
        pause()
        return

    clear()
    console_log.info(f"Past file: {past_path}")
    console_log.info(f"Future file: {future_path}")
    results = makeComparison(past_users, future_users)
    output_comparison_results(results)


def configure_browser_login() -> None:
    """
    Launches browser in non-headless mode for the user to log in manually.
    """
    driver = TwitterDriver(headless=False)
    driver.initialize_driver()  
    print(Fore.YELLOW + "Log in to Twitter in the opened browser.\nPress ENTER here once done..." + Style.RESET_ALL)
    pause()
    driver.quit()


def ask_headless_mode() -> bool:
    """
    Asks user whether to run browser in headless mode.
    Returns:
        bool: True if headless, False otherwise.
    """
    while True:
        clear()
        choice = input("Run browser in headless mode? [Y/n] (default: Y): ").lower()
        if choice == "n":
            return False
        elif choice in ("y", ""):
            return True


def ask_mode_selection() -> MODE:
    """
    Asks user whether to scrape 'following' or 'followers'.
    Returns:
        MODE: Selected scraping mode.
    """
    while True:
        clear()
        choice = input("Which follow you want to operate?\n[1] Following (default)\n[2] Followers\n> ").lower()
        match choice:
            case "2" | "followers":
                return MODE.followers
            case "1" | "following" | "":
                return MODE.following


def output_comparison_results(record: ComparisonResults) -> None:
    """
    Outputs the result of a comparison to the terminal.
    Args:
        record (ComparisonResults): Result object from comparing records.
    """
    print("\n" + " Missing Users ".center(70, "=") + "\n")
    for user in record.removed:
        print(f"{user} is {Fore.RED}missing!{Style.RESET_ALL}")
    if not record.removed:
        print(Fore.LIGHTCYAN_EX + "No users removed." + Style.RESET_ALL)
    else:
        print(f"\nTotal missing: {Fore.RED} {len(record.removed)} {Style.RESET_ALL}")

    print("\n" + " Added Users ".center(70, "=") + "\n")
    for user in record.added:
        print(f"{user} is{Fore.GREEN} added!{Style.RESET_ALL}")
    if not record.added:
        print(Fore.LIGHTCYAN_EX + "No users added." + Style.RESET_ALL)
    else:
        print(f"\nTotal added: {Fore.GREEN} {len(record.added)} {Style.RESET_ALL}")    
        
    pause()