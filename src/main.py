print("application initialize...")

from core.inputCLI import initialize_new_tracking_process, quick_user_comparison,manual_file_comparison,configure_browser_login, clear
from core import *

def main():  
    while True:
        clear()
        
        print("select which operation you want to choose:\n\n")
        print(Fore.LIGHTCYAN_EX)
        print("[1]. run a new tracking scene")
        print("[2]. compares recent users record")
        print("[3]. file selection from the various list of users records")
        print(Style.RESET_ALL)
        print("\n"+"="*60+"\n")
        print(Fore.LIGHTYELLOW_EX)
        print("[x]. press and enter [x] to exit")
        print("[v]. open browser to set up (recomended for first launch)")
        print(Style.RESET_ALL)
        
        options = {
            "1": initialize_new_tracking_process,
            "2": quick_user_comparison,
            "3": manual_file_comparison,
            "v": configure_browser_login
        }
        
        choice = input('\n\n:').lower()
        if choice in options:
            try:
                clear()
                options[choice]()
            except KeyboardInterrupt:
                pass
        elif 'x' in choice:
            break
        

if __name__ == "__main__":
    main()


    
    

