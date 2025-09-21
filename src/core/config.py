import sys
import os

from pathlib import Path

# Determine application path for frozen executables (e.g., PyInstaller)
if getattr(sys, 'frozen', False):
    CURRENT_DIR = Path(os.path.dirname(sys.executable))
else:
    CURRENT_DIR = Path.cwd()

USER_PROFILE_DIR = CURRENT_DIR / "profile"
USER_RECORDS_DIR = CURRENT_DIR / "records"
LOG_FILE_PATH = CURRENT_DIR / "logging.log"

# Scraping constants
SCRAPE_TIMEOUT = 10
MAX_EMPTY_SCROLLS = 20
