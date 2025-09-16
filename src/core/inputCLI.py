# import tkinter
# from tkinter import filedialog
from core.twitterDriver import TwitterDriver
from core.userHandling import *

# from . import UserRecordsNotExists

# set the cli logging
consoleLog = logging.getLogger("console")

# TODO: better cli and UX
def fileSelection(directory: Path, msg: str = "") -> Path:
    """
    Lists files in a given directory and allows the user to select one.
    Returns the full path of the selected file, or None if no file is selected.
    """
    files = returnAllRecords(path=directory)
    consoleLog.info(f"total files : {len(files)}")
    while True:
        clear()
        print(f"{msg}\n\nuser directory : \n{directory}\n")
        for i, file_name in enumerate(files):
            print(f"{i + 1}. {file_name}")
        try:
            choice = int(input("Enter the number of the file to select:"))
            index = choice - 1
            if 0 <= index < len(files):
                clear()
                return files[index]
            else:
                continue
        except ValueError:
            continue


# TODO: do better exception handling
def initializeNewTrackingProcess():
    # configure the settings for scraping operations
    mode = optionsWhichFollows()
    headless = optionsBrowserHeadless()
    clear()
    
    try:
        # initializing the drivers
        twitterScraper = TwitterDriver(headless=headless,mode=mode)
        twitterScraper.initialize_driver()

        #scrape the user follows
        users_follows = twitterScraper.scrape_user_follows()
        username = twitterScraper.username # fetch the username for the users records dir
    except Exception as e:
        consoleLog.error(f"failed to initialize drivers.. make sure you had good internet connection\n{e}")
        pause()
        return
    finally:
        twitterScraper.quit()
    
    # saving the users records and make comparison
    saveUsersRecord(username,mode,users_follows)
    try:
        results = compareRecentRecords(username,mode)
        outputComparisonResults(results)
    except (NotEnoughUserRecords, UserRecordsNotExists, FiledecodeError):
        pause()
        
def quickUserComparison():
    """input the username and which records to make comparison out off"""
    username = input("which user records to compare?\n\n:").lower()
    mode = optionsWhichFollows()
    
    # get the comparison results, skip if not sufficient
    try:
        result = compareRecentRecords(username,mode)
    except (NotEnoughUserRecords, UserRecordsNotExists, FiledecodeError):
        pause()
        return
    
    # output the results
    outputComparisonResults(record=result)

# TODO: there must be a cleaner way to do this right?
def manualFileComparison():
    # configure which users you want to choose
    username = input("which users you want to compare?").lower()
    mode = optionsWhichFollows()
    
    # check if path exist
    userPath = USER_RECORDS_DIR / username / mode
    if not userPath.exists or not username:
        consoleLog.error(f"no users records exist in dir: {USER_RECORDS_DIR / username / mode}")
        pause()
        return

    try:
        pastUserPath = fileSelection(userPath,msg="select the users past records")
        usersPast = readFromRecords(pastUserPath)
                
        futureUserPath = fileSelection(userPath,msg="select the users future records")
        usersFuture = readFromRecords(futureUserPath)
        
        clear()
        consoleLog.info(f"past files selected: {pastUserPath}")
        consoleLog.info(f"future files selected: {futureUserPath}")
    except (UserRecordsNotExists, FileNotFoundError):
        pause()
        return

    results = makeComparison(usersPast,usersFuture)
    outputComparisonResults(results)  

def configuringBrowsers():
    driver = TwitterDriver(headless=False)
    driver.initialize_driver
    print("\nsetting up browser profile for twitter scrape to work..\nafter finishing the login process press enter to quit\n")
    pause()
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
    """specify which users follow to scrape"""
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
    
    pause()