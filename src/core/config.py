import sys
import os

from dotenv import load_dotenv
from pathlib import Path

from core.utils import get_env_variable_int

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

# set var constants
SCRAPE_TIMEOUT = get_env_variable_int("SCRAPE_TIMEOUT", 10)
MAX_EMPTY_SCROLLS = get_env_variable_int("MAX_EMPTY_SCROLLS", 30)
