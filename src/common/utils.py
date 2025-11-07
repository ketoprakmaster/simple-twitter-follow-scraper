import os
import logging

utilsLog = logging.getLogger("utils")

def clear():
    """Cross-platform CLI clearing."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause(msg: str = "\nPress Enter to continue..."):
    """Pauses until any key is pressed."""
    input(msg)
