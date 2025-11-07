from os import getenv
from dotenv import load_dotenv

from common.utils import getenv_int
from config.paths import ENV_FILE_PATH

# load the environment variables if exists
load_dotenv(dotenv_path=ENV_FILE_PATH)

# set var constants
SCRAPE_TIMEOUT = getenv_int("SCRAPE_TIMEOUT", 10)
MAX_EMPTY_SCROLLS = getenv_int("MAX_EMPTY_SCROLLS", 30)

class TwitterSelectors:
    """
    Holds the XPath selectors for scraping Twitter.
    Values can be overridden by setting corresponding environment variables.
    """

    # Default selector for the profile link/button
    ACCOUNT_MENU_BUTTON = getenv(
        "SELECTOR_ACCOUNT_MENU", "//a[@data-testid='AppTabBar_Profile_Link']"
    )

    # Default selector for the user cell in a followers/following list
    USER_CELL = getenv(
        "SELECTOR_USER_CELL", "//button//a[@role='link' and @tabindex='-1']//span"
    )

    # Default selector for the follower/following count on a profile
    FOLLOW_COUNT = getenv(
        "SELECTOR_FOLLOW_COUNT", "//a[contains(@href,'{mode}')]/span[1]"
    )
