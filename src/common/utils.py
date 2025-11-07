import os
import logging

utilsLog = logging.getLogger("utils")

def clear():
    """Cross-platform CLI clearing."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause(msg: str = "\nPress Enter to continue..."):
    """Pauses until any key is pressed."""
    input(msg)

def getenv_int(var_name: str, default_value: int) -> int:
    """Gets an environment variable, converts it to int, and handles errors."""
    value_str = os.getenv(var_name)
    if value_str is None:
        return default_value

    try:
        return int(value_str)
    except (ValueError, TypeError):
        return default_value
