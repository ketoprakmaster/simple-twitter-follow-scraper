from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from colorama import Fore, Style

from selenium.webdriver.wpewebkit.webdriver import WebDriver
import undetected_chromedriver as uc
import logging
import time
import random

from config.paths import USER_PROFILE_DIR, CURRENT_DIR
from common.types import MODE
from common.decorators import timing_decorator
from common.exceptions import UserScrapeOperationFailed
from core.twitterConfig import TwitterSelectors, SCRAPE_TIMEOUT, MAX_EMPTY_SCROLLS

class TwitterDriver:
    def __init__(self, headless: bool = False, mode: MODE = MODE.following):
        """
        TwitterDriver handles scraping Twitter user follows via Selenium automation.

        Args:
            headless (bool): Whether to run the browser in headless mode.
            mode (MODE): Mode of scraping, either 'following' or 'followers'.
        """
        self.username: str
        self.driver : WebDriver
        self.headless: bool = headless
        self.mode: MODE = mode
        self.driver_log = logging.getLogger("driver")
        self._users_list : set[str] = set()

    @timing_decorator(msg="initializing drivers")
    def initialize_driver(self) -> None:
        """
        Initializes the Selenium Chrome driver with undetected-chromedriver.
        Loads user profile and proxy if available.
        """
        if USER_PROFILE_DIR.exists():
            self.driver_log.info(f"current users profile : {USER_PROFILE_DIR}")
        else:
            self.driver_log.warning("no users profile detected, it will generated a new one instead")

        self.driver_log.info("Initializing new driver")
        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={USER_PROFILE_DIR}")
        options.add_argument('--disable-blink-features=AutomationControlled')

        proxy = self.get_proxy()
        if proxy:
            self.driver_log.info(f"proxy selected: {proxy}")
            options.add_argument(f"--proxy-server={proxy}")

        if self.headless:
            options.add_argument("--headless")
            options.add_argument("--headless=new")

        self.driver = uc.Chrome(options=options) # pyright: ignore

    @timing_decorator(msg="fetching user handles")
    def get_user_handle(self) -> str:
        """
        Fetches the logged-in Twitter username by accessing the homepage.
        Sets `self.username` if successful.
        """
        if hasattr(self, "username"):
            self.driver_log.info(f"Username already acquired: {self.username}")
            return self.username

        self.driver_log.info("Getting user handle")
        self.driver.get("https://x.com/home")
        try:
            element = WebDriverWait(self.driver, SCRAPE_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, TwitterSelectors.ACCOUNT_MENU_BUTTON))
            )
        except TimeoutException:
            raise UserScrapeOperationFailed("Timeout: No user login detected. Log in to Twitter first.")

        self.username = str(element.get_attribute("href")).split('/')[-1]
        self.driver_log.info(f"User handle acquired: {self.username}")
        return self.username

    def scroll_down(self) -> None:
        """
        Scrolls down the webpage by twice the window height.
        Helps in lazy-loading Twitter follow elements.
        """
        window_height = self.driver.execute_script("return window.innerHeight;")
        current_scroll = self.driver.execute_script("return window.pageYOffset;")
        target_scroll = current_scroll + (window_height * 2)
        self.driver.execute_script(f"window.scrollTo(0, {target_scroll});")

    @timing_decorator(msg="scraping users")
    def scrape_user_follows(self) -> set[str]:
        """
        Scrapes the users that the logged-in account is following (or its followers).
        Automatically scrolls and accumulates all visible users.

        Returns:
            Set[str]: A set of Twitter handles scraped.

        Raises:
            UserScrapeOperationFailed: If no users are scraped.
        """
        self.get_user_handle()
        self.driver_log.info(f"Scraping {self.username} [{self.mode}]")

        self.driver.get(f"https://x.com/{self.username}/{self.mode}")
        empty_scrolls = 0

        while empty_scrolls <= MAX_EMPTY_SCROLLS:
            new_users = self._scrape_users_on_page()
            diff = self._update_users_list(new_users=new_users)

            if not diff:
                empty_scrolls += 1
            else:
                empty_scrolls = 0

            self.scroll_down()

        if not self._users_list:
            raise UserScrapeOperationFailed("No users were scraped.")

        self.driver_log.info(f"Total users scraped: {len(self._users_list)}")
        return self._users_list

    def _update_users_list(self, new_users: set[str]) -> bool:
            """Custom method to update the list AND print the side effect.
            returns a bool (true) if users has changes/added
            """
            diff = new_users - self._users_list

            if diff:
                for user in diff:
                    self._users_list.add(user)
                    print(f"{user.ljust(50, '.')}:{Fore.CYAN}added ({len(self._users_list)}){Style.RESET_ALL}")

            return any(diff)

    def _scrape_users_on_page(self) -> set[str]:
        """
        Helper method to extract visible Twitter handles from the current page.

        Returns:
            Set[str]: A set of lowercased Twitter handles.

        Raises:
            NoSuchElementException: If no expected elements are found.
        """
        time.sleep(0.2)
        users = set()
        user_elements = WebDriverWait(self.driver, SCRAPE_TIMEOUT).until(
            EC.presence_of_all_elements_located((By.XPATH, TwitterSelectors.USER_CELL))
        )

        for el in user_elements:
            try:
                lines = el.text
                if "@" in lines:
                    users.add(lines.lower())
            except StaleElementReferenceException:
                continue

        return users

    def check_user_follow(self, username: str | None = None, option: MODE = MODE.following) -> int:
        """
        Check the number of followers or following from a user's profile page.\n
        if username isn't provided it will check the current log in users instead
        Args:
            username (str, optional): path to the users profile section.. Defaults to None.
            option (MODE): fetch the chosen user follows. Defaults to MODE.following.

        Returns:
            int: The numeric count of followers/following.
        NOTE: Currently unused and untested.
        """
        if not username:
            username = self.get_user_handle()

        self.driver_log.info(f"start fetching {username} follows")
        self.driver.get(f"https://x.com/{username}")

        elem = WebDriverWait(self.driver,SCRAPE_TIMEOUT).until(
            EC.presence_of_element_located(By.XPATH, TwitterSelectors.FOLLOW_COUNT.format(option)) # pyright: ignore
        )

        count = ''.join(char for char in elem.text if char.isdigit())
        return int(count)

    def get_proxy(self) -> str | None:
        """Retrieves a proxy from 'proxy_list.txt' if available.

        Returns:
            (str, None): A proxy address, or None if unavailable or file is malformed.

        NOTE: Currently unused and untested.
        """
        proxy_file_path = CURRENT_DIR / "proxy_list.txt"
        if not proxy_file_path.exists():
            self.driver_log.warning(f"Proxy file not found: {proxy_file_path}")
            return None

        with open(proxy_file_path, "r") as f:
            proxies = [line.strip() for line in f if line.strip()]

        if not proxies:
            self.driver_log.warning("Proxy list is empty.")
            return None

        return random.choice(proxies)

    def quit(self) -> None:
        """close the selenium browser if it had already exists"""
        if hasattr(self, "driver"):
            self.driver_log.info("closing the browser")
            self.driver.quit()
        else:
            self.driver_log.info("browser had already been closed")
