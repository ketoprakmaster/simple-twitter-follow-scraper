print("application initialize...")

from core.inputCLI import inittialze_tracking_process,quickUserComparison,manual_file_comparison,setting_up_browser, clear
from core import UserScrapeOperationFailed, NotEnoughUserRecords, FiledecodeError

def main():  
    while True:
        clear()
        
        print("select which operation you want to choose:\n\n")
        print("[1]. run a new tracking scene")
        print("[2]. compares recent users record")
        print("[3]. file selection from the various list of users records")
        print("\n"+"="*60+"\n")
        print("[x]. press and enter [x] to exit")
        print("[v]. open browser to set up (recomended for first launch)")
        
        options = {
            "1": inittialze_tracking_process,
            "2": quickUserComparison,
            "3": manual_file_comparison,
            "v": setting_up_browser
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


    
    

