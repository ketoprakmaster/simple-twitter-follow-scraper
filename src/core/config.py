import sys
import os
import logging

from dotenv import load_dotenv
from pathlib import Path

# define files path constants
if getattr(sys, 'frozen', False):
    CURRENT_DIR = Path(os.path.dirname(sys.executable))
else:
    CURRENT_DIR = Path.cwd()

USER_PROFILE_DIR = CURRENT_DIR / "profile"
USER_RECORDS_DIR = CURRENT_DIR / "records"
LOG_FILE_PATH = CURRENT_DIR / "logging.log"
ENV_FILE_PATH = CURRENT_DIR / "config.env"

# load the environment variables if exists
load_dotenv(dotenv_path=ENV_FILE_PATH)

# set the file handlers
filelog = logging.FileHandler(filename=LOG_FILE_PATH)
fileFormatter = logging.Formatter(
    "%(name)-10s: %(asctime)s - %(levelname)-8s -  %(filename)s:%(lineno)s   >>> %(message)s"
)
filelog.setFormatter(fileFormatter)

# set the stream handler
stdout = logging.StreamHandler()
consoleFormatter = logging.Formatter("[%(levelname)s] %(message)s ")
stdout.setFormatter(consoleFormatter)

# add the handlers to the root loggers
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)
rootLogger.addHandler(stdout)
rootLogger.addHandler(filelog)

def get_env_variable(var_name: str, default_value: int) -> int:
    """Gets an environment variable, converts it to int, and handles errors."""
    value_str = os.getenv(var_name)
    if value_str is None:
        return default_value
    
    try:
        return int(value_str)
    except (ValueError, TypeError):
        logging.warning(
            f"Invalid value for '{var_name}': '{value_str}'. "
            f"Falling back to default value: {default_value}."
        )
        return default_value

# set var constants
SCRAPE_TIMEOUT = get_env_variable("SCRAPE_TIMEOUT", 10)
MAX_EMPTY_SCROLLS = get_env_variable("MAX_EMPTY_SCROLLS", 30)

logging.info(f"Configuration loaded: SCRAPE_TIMEOUT={SCRAPE_TIMEOUT}, MAX_EMPTY_SCROLLS={MAX_EMPTY_SCROLLS}")