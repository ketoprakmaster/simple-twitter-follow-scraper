# from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

import undetected_chromedriver as uc
from core import *

# set the logging
driverLog = logging.getLogger("driver")

def initialize_driver(headless:bool = False):
    """initialize new drivers, also checks for proxy if available"""
    driverLog.info(f"initializing new driver")
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={USER_PROFILE}")
    options.add_argument('--disable-blink-features=AutomationControlled')
    proxy = get_proxy()
    if (proxy): 
        options.add_argument(f"--proxy-server:{proxy}")
    if headless:
        options.add_argument(f"--headless")
        options.add_argument(f"--headless=new")
    driver = uc.Chrome(options=options)
    return driver

def get_user_handle(driver) -> str:
    """get the user handle from twitter on an instance of driver web"""
    driverLog.info("getting user handle")
    driver.get("https://x.com/home")
    try:
        element = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.XPATH,"//button[@aria-label='Account menu']//*[@data-testid]"))
        )
    except TimeoutException:
        raise UserScrapeOperationFailed("\ntimeout exception, possibly due to no user login exist yet\nplease ensure that your logins on twitter exist in order to scrape successfully.")
    user_handle = element.get_attribute("data-testid").split('-')[-1]
    driverLog.info(f"user handle acquired: {user_handle}")
    return user_handle

def scroll_down(driver):
    # Calculate the height to scroll (scrolling halfway)
    window_height = driver.execute_script("return window.innerHeight;")

    # Calculate the initial and target scroll positions
    initial_scroll_position = driver.execute_script("return window.pageYOffset;")
    target_scroll_position = initial_scroll_position + (window_height * 2)

    # Scroll halfway down
    driver.execute_script(f"window.scrollTo(0, {target_scroll_position});")    

def scrape_user_follows(username: str, mode: MODE ,driver) -> set:
    """scrape a users follows as it scrolls down the webpages
    
    required args: driver (chrome), username (str), and mode (MODE) a user dir/pointer. 
    Returns a (set) containing 'Hopefully' the entire user follows.
    
    Raise Errors if users_list (set) is empty.
    """
    driverLog.info(f"start scraping {username} {mode}'s ")
    driver.get(f"https://x.com/{username}/{mode}")
    users_list, count = set(),int()
    while True:
        try:
            users = scrape_users_on_page(driver)
        except NoSuchElementException:
            driverLog.error("\nno such element is detected..proceed to refreshing the webpage\n")
            driver.refresh();time.sleep(4)
            continue
        for user in users.difference(users_list):
            users_list.add(user)
            count = 0   # set the count to zero
            print(f"{user.ljust(50,'.')}: added ({len(users_list)})")
        else:
            count += 1  # increment the count by one
            if count <= 20:
                scroll_down(driver)
                continue
            else:
                break  
    # Extract the user elements
    if not users_list:
        raise UserScrapeOperationFailed("no user has been scraped...")
    
    driverLog.info(f"users scraped: {len(users_list)}")
    return users_list

def scrape_users_on_page(driver) -> set:
    """scrape the user elements on page. required args driver (chrome) returns a (set) containing user handles"""
    time.sleep(.2)  # Adjust sleep time as needed
    users, exceptlist = set(), list()
    user_elements = WebDriverWait(driver,10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='cellInnerDiv']"))
    )
    if not user_elements:
        raise NoSuchElementException("no element is detected within webpages")
    for elements in user_elements:
        # mitigates stale element exception
        try:
            elements = elements.text.split('\n')
        except StaleElementReferenceException as e:
            exceptlist.append(e)
            continue
        if len(elements) <= 1:
            # print(f"not enough user elements to scrape out of: {elements}")
            continue
        users_handle : str = elements[1]
        if not users_handle:
            continue
        users.add(users_handle.lower())
    if exceptlist:
        driverLog.warning(f"number of stale element exception occured: {len(exceptlist)}")
        
    return users

def check_user_follow(driver,href) -> int:
    """check users following on the webpage. 
    required an args of both selenium driver (chrome) and href (str) for element location.
    returns a number of follow as an int"""
    driver.get(f"https://x.com/{href.split('/')[0]}")
    time.sleep(5)
    elem = driver.find_element(By.XPATH,f"//a[translate(@href,'ABCDEFGHIJKLMNOPQERSSTUVWXYZ','abcdefghijklmnopqerstuvwxyz') = '/{href.lower()}']")
    elem = ''.join(n for n in elem.text if n.isdigit())
    
    return int(elem) 

def get_proxy() -> str | None:
    """
    Retrieves a proxy from 'proxy_list.txt'.
    If the file doesn't exist, is empty, or if the list is malformed,
    it returns None. Otherwise, it returns a randomly selected proxy string.
    """
    proxy_file_path = Path.cwd() / "proxy_list.txt"
    
    if not proxy_file_path.exists():
        driverLog.warning(f"Proxy file not found at {proxy_file_path}")
        return None
    
    with open(proxy_file_path, "r") as f:
        # Read all lines and strip whitespace, filter out empty lines
        proxies = [line.strip() for line in f if line.strip()]  
        
    if not proxies:
        driverLog.warning(f"Proxy file '{proxy_file_path}' is empty or contains no valid proxies.")
        return None
    
    # Return a randomly selected proxy from the list
    return random.choice(proxies)
            
