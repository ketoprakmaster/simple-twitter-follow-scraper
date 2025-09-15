# import tkinter
# from tkinter import filedialog
from core.twitterDriver import *
from core.userHandling import *

# from . import UserRecordsNotExists

# set the cli logging
consoleLog = logging.getLogger("console")

def file_selection(directory: Path) -> Path:
    """
    Lists files in a given directory and allows the user to select one.
    Returns the full path of the selected file, or None if no file is selected.
    """
    files = [file for file in directory.glob("*") if file.is_file()]
    if not files:
        consoleLog.error(f"No files found in '{directory}'.")
        raise UserRecordsNotExists(f"no files exists in : {directory}")
    consoleLog.info(f"total files : {len(files)}")
    while True:
        clear()
        print(f"user directory : \n{directory}\n")
        for i, file_name in enumerate(files):
            print(f"{i + 1}. {file_name}")
        try:
            choice = int(input("Enter the number of the file to select:"))
            index = choice - 1
            if index < len(files):
                consoleLog.info(f"files selected: {files[index]} at index: {index}")
                return files[index]
            else:
                continue
        except ValueError:
            continue


# TODO: do better exception handling
def inittialze_tracking_process():
    # configure the settings for scraping operations
    mode = optionsWhichFollows()
    headless = optionsBrowserHeadless()
    
    # initializing the drivers
    clear()
    driver = initialize_driver(headless)
    
    # fetch the usernames of logged in twitter accounts
    username = get_user_handle(driver)
    
    #scrape the user follows
    users_follows = scrape_user_follows(username,mode, driver)
    driver.quit()
    
    # saving the users records
    save_users_record_to_path(username,mode,users_follows)
    results = compare_recent_records(username,mode)
    outputComparisonResults(results)
        
def quickUserComparison():
    """input the username and which records to make comparison out off"""
    username = input("which user records to compare?\n\n:").lower()
    mode = optionsWhichFollows()
    
    # get the comparison results
    result = compare_recent_records(username,mode)
    
    # output the results
    outputComparisonResults(record=result)

# TODO: there must be a cleaner way to do this right?
def manual_file_comparison():
    # configure which users you want to choose
    username = input("which users you want to compare?").lower()
    mode = optionsWhichFollows()
    
    # check if path exist
    userPath = USER_RECORDS / username / mode
    if not userPath.exists or not username:
        consoleLog.error(f"no users records exist in dir: {USER_RECORDS / username / mode}")
        input()
        return

    try:
        print("select the past user records")
        past_user_list = file_selection(userPath)
        past_user_list = read_from_record(past_user_list)
                
        print("select the future/current user records")
        future_user_list = file_selection(userPath)
        future_user_list = read_from_record(future_user_list)
    except UserRecordsNotExists:
        input()
        return

    results = makeComparison(past_user_list,future_user_list)
    outputComparisonResults(results)  

def setting_up_browser():
    driver = initialize_driver()
    print("\nsetting up browser profile for twitter scrape to work..\nafter finishing the login process press enter to quit\n")
    input()
    driver.quit()  

def optionsBrowserHeadless() -> bool:
    """chosing and configure the browsers options"""
    while True:
        clear()
        # run the browser as headless or not (default true)
        choice = input("run browser as headless? [y/n] [default: true] :").lower()
        if "n" in choice:
            headless = False
            break
        elif "y" in choice or not choice:
            headless = True
            break
        continue
    return headless
        
def optionsWhichFollows() -> MODE:
    """sprcify which users follow to scrape"""
    while True:
        clear()
        match input("which users follows you choose\n[1]. following (default)\n[2]. followers\n:").lower():
            case "1" | "following" | "":
                mode = MODE.following
            case "2" | "followers": 
                mode = MODE.followers
            case _:
                continue
        break
    return mode


def outputComparisonResults(record: comparisonResults) -> None:
    """requires an argument (comparisonResults) for showing changes and output it onto a terminal"""
    # ouput an user that is missing
    print("\n"+" Missings Users : ".center(70,"="))
    for user in record.removed:
        print(f"{user} is missing!")       
    if not record.removed:
        print("no compared users that are missing..\n")
    else:
        print(f"\ntotal missing users: {len(record.removed)}\n")
     
    # ouput an user that is added
    print(" Added Users : ".center(70,"=")) 
    for user in record.added:
        print(f"{user} is added!")

    if not record.added:
        print("no compared users that are added..\n")
    else:
        print(f"\ntotal added users: {len(record.added)}\n")
    
    input()