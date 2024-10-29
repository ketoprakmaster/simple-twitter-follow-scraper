import tkinter
import os
import time

from pathlib import Path
from tkinter import filedialog
# from twitterConfig import config

# conf = config()

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


def options_for_which_follow(string) -> str | None: # either returns "following" or "followers" or None
    print(string)
    print("\n[1]. following\n[2]. followers\n\n")
    while True:
        match input(":").lower():
            case "1" | "following": 
                mode = "following"
            case "2" | "followers": 
                mode = "followers"
            # case _ if conf.return_value(key="lastoperation"):
            #     mode = conf.return_value(key="lastoperation")
            case _:
                continue
        
        # conf.set_config(key="lastOperation",value=mode)   
        return mode



def options_username_input(msg: str = '') -> str:
    if msg:
        print(msg)
    
    username: str = ''
    while not username:
        username = input(":")
    
    return username.lower()



def options_yes_or_no(string) -> str: # by default just pressing enter counts as "yes"
    while True:
        # os.system('cls')
        try:
            match input(string):
                case "no" | "n":
                    return False
                case _:
                    return True
        except Exception as e:
            print(e)



if __name__ == "__main__":
    print(options_for_which_follow())