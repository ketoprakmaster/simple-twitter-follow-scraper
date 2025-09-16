from core.twitterDriver import TwitterDriver
from core.userHandling import (
    compareRecentRecords,
    saveUsersRecord,
    readFromRecords,
    returnAllRecords,
    makeComparison
)
from . import *

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
        for i, file_name in enumerate(files):
            print(f"{i + 1}. {file_name}")
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

    saveUsersRecord(username, mode, users)
    try:
        results = compareRecentRecords(username, mode)
        output_comparison_results(results)
    except (NotEnoughUserRecords, UserRecordsNotExists, FiledecodeError):
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


def configure_browser_login():
    """
    Launches browser in non-headless mode for the user to log in manually.
    """
    driver = TwitterDriver(headless=False)
    driver.initialize_driver()  # ← THIS WAS A BUG! Previously it was missing ()
    print("Log in to Twitter in the opened browser.\nPress ENTER here once done...")
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
        choice = input("Which mode to scrape?\n[1] Following (default)\n[2] Followers\n> ").lower()
        match choice:
            case "2" | "followers":
                return MODE.followers
            case "1" | "following" | "":
                return MODE.following


def output_comparison_results(record: comparisonResults) -> None:
    """
    Outputs the result of a comparison to the terminal.
    Args:
        record (comparisonResults): Result object from comparing records.
    """
    print("\n" + " Missing Users ".center(70, "="))
    for user in record.removed:
        print(f"{user} is missing.")
    if not record.removed:
        print("No users removed.")
    else:
        print(f"\nTotal missing: {len(record.removed)}")

    print("\n" + " Added Users ".center(70, "="))
    for user in record.added:
        print(f"{user} is added.")
    if not record.added:
        print("No users added.")
    else:
        print(f"\nTotal added: {len(record.added)}")
    
    pause()
