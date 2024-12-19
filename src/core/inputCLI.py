import tkinter
import os
import time

from pathlib import Path
from tkinter import filedialog
from core.twitterDriver import *
from core.userHandling import *

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
    os.system("cls")
    driver = ''
    try:
        options = options_yes_or_no("run browser in headless mode? (y/n)")
        mode = options_for_which_follow()
        driver = initialize_driver(options)
        username = get_user_handle(driver)
        userpath = f"{username}/{mode}"
        users_follows = scrape_user_follows(userpath, driver)
        save_and_compare_user_follows(userpath,users_follows)
    except NoSuchWindowException:
        print("\nno windows is detected,aborting the program")
        return  
    except UserScrapeOperationFailed as e:
        print(e)
        return
    except KeyboardInterrupt:
        pass
    finally:
        if driver:driver.quit()
    
def save_and_compare_user_follows(user_path: str,users_set: set):
    try:
        users_dict = users_records_comparison(
            users_past = read_from_recent_user_records(user_path),
            users_future = users_set
        )
    except FileNotFoundError as e:
        print(e)
        save_users_record_to_path(user_path,users_set)
    output_users_changes(users_dict)
    save_users_record_to_path(user_path,users_set)
    save_accumulated_records(user_path)   
 
def check_recent_comparison(user_path:str = ''):
    #input the specified target
    if not user_path:
        username = input("which user records to compare?").lower()
        mode = options_for_which_follow("\nwhich user follow you want to compare?")
        
        user_path = f"{username}/{mode}"
    
    # retrieve all users records from given user_path
    try:
        all_records = returns_atleast_two_user_records(user_path)
    except (FileNotFoundError, notEnoughFileToCompare) as e:
        print(e)
        return
    
    past_user_list = read_from_record(all_records[-2])
    current_user_list = read_from_record(all_records[-1])
    
    users = users_records_comparison(past_user_list,current_user_list)
    output_users_changes(users)
  
def manual_file_comparison():
    os.system("cls")
    print("select your past records for comparison\n")    
    past_user_list = read_from_record(file_selection())

    print("select your future records for comparison\n")
    future_user_list = read_from_record(file_selection())
            
    users_changes = users_records_comparison(past_user_list,future_user_list)
    output_users_changes(users=users_changes)

def setting_up_browser():
    os.system("cls")
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
                print("try again")
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
