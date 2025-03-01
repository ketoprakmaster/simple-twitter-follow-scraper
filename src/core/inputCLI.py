import tkinter
from tkinter import filedialog
from core.twitterDriver import *
from core.userHandling import *
from core import clear

def file_selection() -> Path:
    while True:
        try:
            root = tkinter.Tk()
            root.withdraw()  # Hide the main tkinter window
            root.wm_attributes('-topmost', 1) 
            file = filedialog.askopenfilename(initialdir=Path.cwd())

            if not file or not os.access(file, os.R_OK) or not file.endswith('txt'):
                print("please choose a file ")
                continue
            
            print(file)
            return Path(file)
        
        except FileNotFoundError:
            print("file not found!")
        except Exception as e:
            print(e)
            time.sleep(2)
            continue

def inittialze_tracking_process(): 
    driver = ''
    try:
        options = options_yes_or_no("run browser in headless mode? (y/n)")
        mode = options_for_which_follow()
        driver = initialize_driver(options)
        username = get_user_handle(driver)
        userpath = f"{username}/{mode}"
        users_follows = scrape_user_follows(userpath, driver)
        save_users_record_to_path(userpath,users_follows)
        compare_recent_records(userpath)
    except NotEnoughUserRecords:
        print("not enough users records to be made for comparison..")
        pass
    finally:
        if driver:driver.quit()
    
def check_recent_comparison(userpath:str = ''):
    #input the specified target
    if not userpath:
        username = input("which user records to compare?\n\n:").lower()
        mode = options_for_which_follow("\nwhich user follow you want to compare?")
        
        userpath = f"{username}/{mode}"
    
    compare_recent_records(userpath)
  
def manual_file_comparison():
    print("select your past records for comparison\n")    
    past_user_list = read_from_record(file_selection())

    print("select your future records for comparison\n")
    future_user_list = read_from_record(file_selection())
            
    records_comparison(past_user_list,future_user_list)

def setting_up_browser():
    driver = initialize_driver()
    print("\nsetting up browser profile for twitter scrape to work..\nafter finishing the login process press enter to quit\n")
    input()
    driver.quit()  

def options_for_which_follow(msg: str = "\n[1]. following (default)\n[2]. followers\n") -> str: 
    "either returns 'following' or 'followers' or None"
    print(msg)
    while True:
        match input("\n:").lower():
            case "1" | "following" | "":
                mode = "following"
            case "2" | "followers": 
                mode = "followers"
            case _:
                continue
        break
    return mode

def options_yes_or_no(msg: str = "options (y/n)") -> bool:  
    "by default just pressing enter counts as 'yes'"
    print(msg)
    while True:
        choice =  input("\n:").lower()
        if "y" in choice or not choice:
            return True
        elif "n" in choice:
            return False
        else:
            print("try again")
            continue
