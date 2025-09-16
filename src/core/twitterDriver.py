from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

import undetected_chromedriver as uc
from core import *

class TwitterDriver:
    def __init__(self, headless: bool = False, mode: MODE = MODE.following):
        """
        TwitterDriver handles scraping Twitter user follows via Selenium automation.

        Args:
            headless (bool): Whether to run the browser in headless mode.
            mode (MODE): Mode of scraping, either 'following' or 'followers'.
        """
        self.headless = headless
        self.driver = None
        self.username: str = None
        self.mode: MODE = mode
        self.driver_log = logging.getLogger("driver")

    def initialize_driver(self) -> None:
        """
        Initializes the Selenium Chrome driver with undetected-chromedriver.
        Loads user profile and proxy if available.
        """
        self.driver_log.info("Initializing new driver")
        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={USER_PROFILE_DIR}")
        options.add_argument('--disable-blink-features=AutomationControlled')

        proxy = self.get_proxy()
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")

        if self.headless:
            options.add_argument("--headless")
            options.add_argument("--headless=new")

        self.driver = uc.Chrome(options=options)

    def get_user_handle(self) -> str:
        """
        Fetches the logged-in Twitter username by accessing the homepage.
        Sets `self.username` if successful.
        """
        if self.username:
            self.driver_log.info(f"Username already acquired: {self.username}")
            return self.username

        self.driver_log.info("Getting user handle")
        self.driver.get("https://x.com/home")
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Account menu']//*[@data-testid]"))
            )
        except TimeoutException:
            raise UserScrapeOperationFailed("Timeout: No user login detected. Log in to Twitter first.")

        self.username = element.get_attribute("data-testid").split('-')[-1]
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
        users_list = set()
        empty_scrolls = 0

        while True:
            try:
                new_users = self._scrape_users_on_page()
            except NoSuchElementException:
                self.driver_log.error("No element detected, refreshing page...")
                self.driver.refresh()
                time.sleep(4)
                continue
            # tracked the difference and prints any new users that had been scraped by
            diff = new_users - users_list 
            for user in diff:
                empty_scrolls = 0
                users_list.add(user)
                print(f"{user.ljust(50, '.')} added ({len(users_list)})")
            if not diff:
                empty_scrolls += 1
                if empty_scrolls > 20:
                    break
            else:
                empty_scrolls = 0
            self.scroll_down()
        if not users_list:
            raise UserScrapeOperationFailed("No users were scraped.")

        self.driver_log.info(f"Total users scraped: {len(users_list)}")
        return users_list

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
        user_elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='cellInnerDiv']"))
        )

        for el in user_elements:
            try:
                lines = el.text.split("\n")
                if len(lines) > 1:
                    users.add(lines[1].lower())
            except StaleElementReferenceException:
                continue

        return users

    def check_user_follow(self, href: str) -> int:
        """
        Check the number of followers or following from a user's profile page.

        Args:
            href (str): URL path to the follow section, e.g., 'username/following'.

        Returns:
            int: The numeric count of followers/following.

        NOTE: Currently unused and untested.
        """
        self.driver.get(f"https://x.com/{href.split('/')[0]}")
        time.sleep(5)
        elem = self.driver.find_element(
            By.XPATH,
            f"//a[translate(@href,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz') = '/{href.lower()}']"
        )
        count = ''.join(c for c in elem.text if c.isdigit())
        return int(count)

    def get_proxy(self) -> list[str] | None:
        """
        Retrieves a proxy from 'proxy_list.txt' if available.

        Returns:
            str | None: A proxy address, or None if unavailable or file is malformed.
            
        NOTE: Currently unused and untested.
        """
        proxy_file_path = Path.cwd() / "proxy_list.txt"
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
        if self.driver:
            self.driver_log.info("closing the browser")
            self.driver.quit()
        else:
            self.driver_log.info("browser had already been closed")
