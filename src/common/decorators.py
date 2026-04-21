import logging
import time
import asyncio
import inspect
from functools import wraps

time_log = logging.getLogger("time")

def timing_decorator(msg: str = ""):
    """function decorators for measuring execution time"""
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if inspect.iscoroutinefunction(func):
                async def async_wrapped():
                    start_time = time.perf_counter()
                    result = await func(*args, **kwargs)
                    end_time = time.perf_counter()
                    time_log.info(f"{msg} took {end_time - start_time:.4f} seconds.")
                    return result
                return async_wrapped()
            
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            time_log.info(f"{msg} took {end_time - start_time:.4f} seconds.")
            return result
        return wrapped
    return wrapper
