from decouple import AutoConfig
import sys
import logging

from config.paths import CURRENT_DIR

# setup logger
config_log = logging.getLogger("config")

# load env from specfied files if it exists
config_log.info(f"Using AutoConfig with search_path={CURRENT_DIR}")
env_config = AutoConfig(search_path=CURRENT_DIR)

# pyright: reportAssignmentType=false
class TwitterSelectors:
    """
    Holds the XPath selectors for scraping Twitter.
    Values can be overridden by setting corresponding environment variables.
    """

    # Default selector for the profile link/button
    ACCOUNT_MENU_BUTTON : str = env_config(
        "SELECTOR_ACCOUNT_MENU", cast=str,
        default="a[aria-label='profile' i"
    )

    # Default selector for the user cell in a followers/following list
    USER_CELL : str = env_config(
        "SELECTOR_USER_CELL", cast=str,
        default="button a[tabindex='-1'] span"
    )

    # Default selector for the follower/following count on a profile
    FOLLOW_COUNT : str = env_config(
        "SELECTOR_FOLLOW_COUNT", cast=str,
        default="a[href*='following' i]"
    )

try:
    # How much scroll by how much: 50 = half of page, 100 = a whole page, 200 = twice the page height etc
    SCROLL_AMOUNT: int = env_config(
        "SCROLL_AMOUNT", cast=int, default=300
    )

    #
    SCRAPE_TIMEOUT : int = env_config(
        "SCRAPE_TIMEOUT", cast=int, default=10
    )

    MAX_EMPTY_SCROLLS : int = env_config(
        "MAX_EMPTY_SCROLLS", cast=int, default=30
    )

except (ValueError, NameError) as e:
    config_log.error(f"""failed to load env variables! \n{e}""")
    sys.exit(1)

config_log.info(f"""loaded twitterSelectors
    {TwitterSelectors.ACCOUNT_MENU_BUTTON=}\n {TwitterSelectors.USER_CELL=}\n {TwitterSelectors.FOLLOW_COUNT=}""")
