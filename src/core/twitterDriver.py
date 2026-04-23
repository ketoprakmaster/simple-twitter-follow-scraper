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
    """
    A driver class to handle Twitter scraping using nodriver.

    This class manages the browser lifecycle, handles navigation to Twitter,
    and implements the logic to scrape users from the 'following' or 'followers' lists.
    """
    def __init__(self, headless: bool = False, mode: MODE = MODE.following):
        """
        Initializes the TwitterDriver.

        Args:
            headless (bool): Whether to run the browser in headless mode. Defaults to False.
            mode (MODE): The scraping mode, either MODE.following or MODE.followers. Defaults to MODE.following.
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
        Initializes a Chrome instance via nodriver.

        Configures the browser with the user data directory for session persistence
        and optionally sets up a proxy if available in 'proxy_list.txt'.
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
        Identifies the currently logged-in Twitter user.

        Navigates to the home page and looks for the profile menu button to extract the handle.

        Returns:
            str: The extracted Twitter username.

        Raises:
            UserScrapeOperationFailed: If no user login is detected.
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
        Scrolls the page down to trigger lazy-loading of content.

        Args:
            page (uc.Tab): The current browser tab to scroll.

        Raises:
            DriverNotInitialized: If the driver has not been initialized.
        """
        if not self.driver or not page:
            raise DriverNotInitialized("Initialize Driver first")

        await page.scroll_down(amount=SCROLL_AMOUNT)

    @timing_decorator(msg="scraping users")
    async def scrape_user_follows(self) -> set[str]:
        """
        Scrapes the following or followers list of the logged-in user.

        The method navigates to the relevant profile page, iteratively scrolls down,
        and collects unique user handles until no new users are found for a set number of scrolls.

        Returns:
            set[str]: A set of lowercased Twitter handles scraped.

        Raises:
            UserScrapeOperationFailed: If no users could be scraped.
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
            """
            Updates the internal user set with newly discovered handles.

            Returns:
                bool: True if any new users were added, False otherwise.
            """
            diff = new_users - self._users_list

            if diff:
                for user in diff:
                    self._users_list.add(user)
                    print(f"{user.ljust(50, '.')}:{Fore.CYAN}added ({len(self._users_list)}){Style.RESET_ALL}")

            return any(diff)

    async def _scrape_users_on_page(self, page: uc.Tab) -> set[str]:
        """
        Extracts visible user handles from the current page content.

        Args:
            page (uc.Tab): The browser tab to scrape.

        Returns:
            set[str]: A set of discovered lowercased Twitter handles.
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
        Retrieves the count of followers or following for a specified user.

        Args:
            username (str, optional): The Twitter handle to check. If None, checks the logged-in user.
            option (MODE): Whether to fetch followers or following. Defaults to MODE.following.

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
        """
        Ensures a page is fully loaded by waiting for a specific element to appear.

        Args:
            page (uc.Tab): The browser tab to monitor.
            attempt (int): Number of retry attempts. Defaults to 5.
            selector (str): The CSS selector to wait for. Defaults to "span".

        Raises:
            UserScrapeOperationFailed: If the element does not appear within the given attempts.
        """
        while attempt:
            try:
                await page.wait_for(selector=selector,timeout=20)
                return
            except uc.ProtocolException as e:
                attempt -= 1
                self.driver_log.warning(f"ProtocolException: page not fully loaded, try again ({attempt=})")

        raise UserScrapeOperationFailed(f"ensure_page_load(): failed to load page: {page.target.url}")


    def get_proxy(self) -> str | None:
        """
        Attempts to retrieve a random proxy from 'proxy_list.txt'.

        Returns:
            str | None: A proxy address if the file exists and is not empty, otherwise None.
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
        """
        Gracefully shuts down the browser driver if it is active.
        """
        if hasattr(self, "driver"):
            self.driver_log.info("closing the browser")
            self.driver.stop() # not an async function no need to be awaited
        else:
            self.driver_log.info("browser had already been closed")
