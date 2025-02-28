print("application initialize...")

from core.inputCLI import inittialze_tracking_process,check_recent_comparison,manual_file_comparison,setting_up_browser, clear


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
            "2": check_recent_comparison,
            "3": manual_file_comparison,
            "v": setting_up_browser
        }
        
        try:
            choice = input('\n\n:').lower()
            if choice in options:
                clear()
                options[choice]()
                input("\n\npress any key to continue")
            elif 'x' in choice:
                break
        except KeyboardInterrupt:
            break



if __name__ == "__main__":
    main()
    
    

