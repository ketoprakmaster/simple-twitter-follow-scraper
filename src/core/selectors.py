from os import getenv

class TwitterSelectors:
    """
    Holds the XPath selectors for scraping Twitter.
    Values can be overridden by setting corresponding environment variables.
    """
    # Default selector for the profile link/button
    ACCOUNT_MENU_BUTTON = getenv(
        'SELECTOR_ACCOUNT_MENU',
        "//a[@data-testid='AppTabBar_Profile_Link']"
    )

    # Default selector for the user cell in a followers/following list
    USER_CELL = getenv(
        'SELECTOR_USER_CELL',
        "//div[@data-testid='UserCell']//a[@tabindex='-1']"
    )

    # Default selector for the follower/following count on a profile
    FOLLOW_COUNT = getenv(
        'SELECTOR_FOLLOW_COUNT',
        "//a[contains(@href,'{mode}')]/span[1]"
    )