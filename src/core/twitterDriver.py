from colorama import Fore, Style
import logging
import asyncio
import random

import nodriver as uc

from config.paths import USER_PROFILE_DIR, CURRENT_DIR
from config.vars import SCROLL_AMOUNT, TwitterSelectors, SCRAPE_TIMEOUT, MAX_EMPTY_SCROLLS
from common.types import MODE
from common.decorators import timing_decorator
from common.exceptions import DriverNotInitialized, UserScrapeOperationFailed

class TwitterDriver:
    def __init__(self, headless: bool = False, mode: MODE = MODE.following):
        """
        TwitterDriver handles scraping Twitter user follows via Nodriver automation.

        Args:
            headless (bool): Whether to run the browser in headless mode.
            mode (MODE): Mode of scraping, either 'following' or 'followers'.
        """
        self.username: str
        self.driver : uc.Browser
        self.page: uc.Tab
        self.headless: bool = headless
        self.mode: MODE = mode
        self.driver_log = logging.getLogger("driver")
        self._users_list : set[str] = set()

    @timing_decorator(msg="initializing drivers")
    async def initialize_driver(self) -> None:
        """
        Initializes the a Chrome Instance through nodriver.start.
        Loads user profile and proxy if available.
        """
        config = uc.Config()

        if USER_PROFILE_DIR.exists():
            self.driver_log.info(f"current users profile : {USER_PROFILE_DIR}")
        else:
            self.driver_log.warning("no users profile detected, it will generated a new one instead")

        self.driver_log.info("Initializing new driver")
        config.user_data_dir = USER_PROFILE_DIR
        config.headless = self.headless

        proxy = self.get_proxy()
        if proxy:
            self.driver_log.info(f"proxy selected: {proxy}")
            config.add_argument(f"--proxy-server={proxy}") # TODO: test proxy

        self.driver = await uc.start(config=config)

    @timing_decorator(msg="fetching user handles")
    async def get_user_handle(self) -> str:
        """
        Fetches the logged-in Twitter username by accessing the homepage.
        Sets `self.username` if successful.
        """
        if hasattr(self, "username"):
            self.driver_log.info(f"Username already acquired: {self.username}")
            return self.username

        self.driver_log.info("Getting user handle")
        tab = await self.driver.get("https://x.com/home")
        await self.ensure_page_load(page=tab, selector=TwitterSelectors.ACCOUNT_MENU_BUTTON)
        element = await tab.select(TwitterSelectors.ACCOUNT_MENU_BUTTON, float(SCRAPE_TIMEOUT))

        if not element:
            raise UserScrapeOperationFailed("get_user_handle(): No user login detected. Log in to Twitter first.")

        # TODO: replace with a dedicated REGEX func
        self.username = str(element.attrs.get('href')).replace("/","").lower()
        self.driver_log.info(f"User handle acquired: {self.username}")
        return self.username

    async def scroll_down(self, page: uc.Tab) -> None:
        """
        Scrolls down the webpage by twice the window height.
        Helps in lazy-loading Twitter follow elements.
        """
        if not self.driver or not page:
            raise DriverNotInitialized("Initialize Driver first")

        await page.scroll_down(amount=SCROLL_AMOUNT)

    @timing_decorator(msg="scraping users")
    async def scrape_user_follows(self) -> set[str]:
        """
        Scrapes the users that the logged-in account is following (or its followers).
        Automatically scrolls and accumulates all visible users.

        Returns:
            Set[str]: A set of Twitter handles scraped.

        Raises:
            UserScrapeOperationFailed: If no users are scraped.
        """
        empty_scrolls = 0

        await self.get_user_handle()
        self.driver_log.info(f"Scraping {self.username} [{self.mode}]")

        page = await self.driver.get(f"https://x.com/{self.username}/{self.mode}")
        await self.ensure_page_load(page=page, selector="[data-testid='usercell' i]")

        while empty_scrolls <= MAX_EMPTY_SCROLLS:
            new_users = await self._scrape_users_on_page(page)
            diff = self._update_users_list(new_users=new_users)

            if not diff:
                empty_scrolls += 1
            else:
                empty_scrolls = 0

            await self.scroll_down(page)

        if not self._users_list:
            raise UserScrapeOperationFailed("scrape_user_follows(): No users were scraped.")

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

    async def _scrape_users_on_page(self, page: uc.Tab) -> set[str]:
        """
        Helper method to extract visible Twitter handles from the current page.

        Returns:
            Set[str]: A set of lowercased Twitter handles.

        Raises:
            NoSuchElementException: If no expected elements are found.
        """
        await page.sleep(.5)
        users = set()
        user_elements = await page.select_all(TwitterSelectors.USER_CELL, SCRAPE_TIMEOUT)

        if not user_elements:
            self.driver_log.warning("No User Element extracted from _scrape_users_on_page!")

        for el in user_elements:
            try:
                lines = el.text
                if "@" in lines: users.add(lines.lower())
            except Exception as e:
                self.driver_log.error("Unexpected Error encountered on _scrape_users_on_page!")

        return users

    async def check_user_follow(self, username: str | None = None, option: MODE = MODE.following) -> int:
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
            username = await self.get_user_handle()

        self.driver_log.info(f"start fetching {username} follows")
        page = await self.driver.get(f"https://x.com/{username}")
        elem = await page.select(TwitterSelectors.FOLLOW_COUNT, SCRAPE_TIMEOUT)

        # TODO: make a dedicated func for int input sanitation
        count = ''.join(char for char in elem.text if char.isdigit())
        return int(count)

    async def ensure_page_load(self, page: uc.Tab, attempt: int = 5, selector: str = "span") -> None:
        """Helper functions to ensure twitter page is properly loaded using Tab.wait_for

        if not try until n many attempts"""

        while attempt:
            try:
                await page.wait_for(selector=selector,timeout=20)
                return
            except uc.ProtocolException as e:
                attempt -= 1
                self.driver_log.warning(f"ProtocolException: page not fully loaded, try again ({attempt=})")

        raise UserScrapeOperationFailed(f"ensure_page_load(): failed to load page: {page.target.url}")


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
        """close the browser if it had already exists"""
        if hasattr(self, "driver"):
            self.driver_log.info("closing the browser")
            self.driver.stop() # not an async function no need to be awaited
        else:
            self.driver_log.info("browser had already been closed")
