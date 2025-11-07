import logging
import time
from functools import wraps

time_log = logging.getLogger("time")

def timing_decorator(msg: str = ""):
    """function decorators for measuring execution time"""
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            time_log.info(f"{msg} took {execution_time:.4f} seconds.")
            return result
        return wrapped
    return wrapper
