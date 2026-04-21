import os
import logging

utilsLog = logging.getLogger("utils")

def clear():
    """Cross-platform CLI clearing."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause(msg: str = "\nPress Enter to continue..."):
    """Pauses until any key is pressed."""
    safe_input(msg)

def safe_input(prompt: str = "") -> str:
    """Helper func for handling KeyboardInterrupt inside of asnyc"""
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        # raise KeyboardInterrupt specifically so the
        # parent 'try/except' blocks can catch it consistently.
        raise KeyboardInterrupt
