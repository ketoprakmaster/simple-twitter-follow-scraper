import os
import time
import logging
from functools import wraps
from pathlib import Path

utilsLog = logging.getLogger("utils")

def clear():
    """Cross-platform CLI clearing."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause(msg: str = "\nPress Enter to continue..."):
    """Pauses until any key is pressed."""
    input(msg)

def timing_decorator(msg: str = ""):
    """function decorators for measuring execution time"""
    def wrapper(func):
        @wraps(func)  
        def wrapped(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            utilsLog.info(f"{msg} took {execution_time:.4f} seconds.")
            return result
        return wrapped
    return wrapper

def get_env_variable_int(var_name: str, default_value: int) -> int:
    """Gets an environment variable, converts it to int, and handles errors."""
    value_str = os.getenv(var_name)
    if value_str is None:
        return default_value
    
    try:
        return int(value_str)
    except (ValueError, TypeError):
        return default_value

