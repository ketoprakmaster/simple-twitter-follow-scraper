from config.paths import USER_RECORDS_DIR
from common.utils import pause, clear, safe_input
from common.exceptions import (
    DriverNotInitialized,
    NotEnoughUserRecords,
    FiledecodeError,
    UserRecordsNotExists,
    UserScrapeOperationFailed
)
from common.types import MODE, ComparisonResults
from core.twitterDriver import TwitterDriver
from core.userHandling import UserSnapshot

from colorama import Style, Fore
from pathlib import Path
import logging

console_log = logging.getLogger("console")


def file_selection(directory: Path, msg: str = "") -> Path:
    """
    Lists files in a given directory and allows the user to select one.
    Returns the selected file path.
    """
    # Using the helper method from a temporary snapshot to get files
    temp_snap = UserSnapshot("", MODE.following, set())
    files = temp_snap._return_all_stored_records(user_path=directory)

    console_log.info(f"Total files: {len(files)}")

    while True:
        clear()
        print(f"{msg}\n\nUser directory: {directory}\n")
        # Ensure they are sorted for the UI
        for i, file in enumerate(sorted(files)):
            print(f"{Fore.CYAN}[{i + 1}]. {file.name}{Style.RESET_ALL}")
        try:
            choice = int(input("Enter the number of the file to select: "))
            if 1 <= choice <= len(files):
                clear()
                return sorted(files)[choice - 1]
        except ValueError:
            continue


async def initialize_new_tracking_process():
    """
    Starts a new Twitter scraping session, saves the user records,
    and compares against previous records using the Snapshot logic.
    """
    mode = ask_mode_selection()
    headless = ask_headless_mode()

    scraper = None
    try:
        scraper = TwitterDriver(headless=headless, mode=mode)
        await scraper.initialize_driver()
        scraped_users = await scraper.scrape_user_follows()
        username = scraper.username

        # 1. Create a snapshot of the current live data
        current_snap = UserSnapshot(username, mode, scraped_users)

        # 2. Try to load the previous snapshot
        try:
            past_snap = UserSnapshot.from_latest(username, mode)
            results = current_snap - past_snap
        except UserRecordsNotExists:
            # First time running for this user
            results = ComparisonResults(added=scraped_users)

        # 3. Handle Investigation & Output
        if results.added or results.removed:
            if results.removed:
                print(f"\n{Fore.YELLOW}Verifying {len(results.removed)} missing users...{Style.RESET_ALL}")
                await results.check_status(driver=scraper)

                # --- RECONCILIATION LOGIC ---
                false_negatives = results.get_false_negatives()
                if false_negatives:
                    # 1. Add them back to the snapshot set so the saved file is accurate
                    current_snap.users.update(false_negatives)

                    # 2. Clean up the results dict so they don't clutter the CLI output
                    for user in false_negatives:
                        del results.removed[user]

            current_snap.save()
            output_comparison_results(record=results)
        else:
            console_log.info("No user changes detected, skipping save.")
            pause()

    except (UserScrapeOperationFailed, DriverNotInitialized) as e:
        console_log.error(f"A problem occurred during scraping:\n{e}")
        pause()
    except Exception as e:
        console_log.error(f"An Error occurred on initialize_new_tracking_process()\n{e}")
        pause()
    finally:
        if scraper:
            scraper.quit()


def quick_user_comparison():
    """
    Quickly compares the two most recent records of a user using Snapshot subtraction.
    """
    username = input("Enter username to compare: ").lower()
    mode = ask_mode_selection()

    try:
        # Create a temp snapshot just to access the record list
        temp = UserSnapshot(username, mode, set())
        all_records = sorted(temp._return_all_stored_records())

        if len(all_records) < 2:
            raise NotEnoughUserRecords("Need at least 2 records for a quick comparison.")

        # Load the two most recent as snapshots
        latest_users = temp._read_from_single_records(all_records[-1])
        past_users = temp._read_from_single_records(all_records[-2])

        now_snap = UserSnapshot(username, mode, latest_users, timestamp=all_records[-1].stem)
        then_snap = UserSnapshot(username, mode, past_users, timestamp=all_records[-2].stem)

        results = now_snap - then_snap
        output_comparison_results(results)

    except (NotEnoughUserRecords, UserRecordsNotExists, FiledecodeError) as e:
        console_log.error(e)
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

        # Load them into snapshots to use the dunder method
        temp = UserSnapshot(username, mode, set())

        past_snap = UserSnapshot(
            username, mode, temp._read_from_single_records(past_path), timestamp=past_path.stem
        )
        future_snap = UserSnapshot(
            username, mode, temp._read_from_single_records(future_path), timestamp=future_path.stem
        )

        clear()
        console_log.info(f"Past file: {past_path.name}")
        console_log.info(f"Future file: {future_path.name}")

        results = future_snap - past_snap
        output_comparison_results(results)

    except (UserRecordsNotExists, FileNotFoundError, FiledecodeError) as e:
        console_log.error(e)
        pause()


def output_comparison_results(record: ComparisonResults) -> None:
    """
    Outputs the result of a comparison to the terminal with Status details.
    """
    print("\n" + " Missing Users ".center(70, "=") + "\n")
    for user, status in record.removed.items():
        # Display the specific status (Banned, Missing, or just Unfollowed/Exists)
        status_color = Fore.RED if status != "Exists" else Fore.YELLOW
        print(f"{user.ljust(30)} -> {status_color}{status}{Style.RESET_ALL}")

    if not record.removed:
        print(Fore.LIGHTCYAN_EX + "No users removed." + Style.RESET_ALL)
    else:
        print(f"\nTotal missing: {Fore.RED}{len(record.removed)}{Style.RESET_ALL}")

    print("\n" + " Added Users ".center(70, "=") + "\n")
    for user in record.added:
        print(f"{user} is {Fore.GREEN}added!{Style.RESET_ALL}")

    if not record.added:
        print(Fore.LIGHTCYAN_EX + "No users added." + Style.RESET_ALL)
    else:
        print(f"\nTotal added: {Fore.GREEN}{len(record.added)}{Style.RESET_ALL}")

    pause()


async def configure_browser_login() -> None:
    """
    Launches browser in non-headless mode for the user to log in manually.
    """
    try:
        driver = TwitterDriver(headless=False)
        await driver.initialize_driver()
        print(Fore.YELLOW + "Log in to Twitter in the opened browser.\nPress ENTER here once done..." + Style.RESET_ALL)
        pause()
    except Exception as e:
        console_log.error(f"an Error occured on initialize_new_tracking_process()\n{e}")
        pause()
        return
    finally:
        if locals().get('driver'):
            driver.quit()


def ask_headless_mode() -> bool:
    """
    Asks user whether to run browser in headless mode.
    Returns:
        bool: True if headless, False otherwise.
    """
    while True:
        clear()
        choice = safe_input("Run browser in headless mode? [Y/n] (default: Y): ").lower()
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
        choice = safe_input("Which follow you want to operate?\n[1] Following (default)\n[2] Followers\n> ").lower()
        match choice:
            case "2" | "followers":
                return MODE.followers
            case "1" | "following" | "":
                return MODE.following
