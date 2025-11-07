# Twitter Follow Scraper

This Python application is designed to scrape Twitter (now X.com) to track changes in a user's "following" or "followers" lists. It leverages Selenium with `undetected_chromedriver` to interact with the Twitter website, allowing for the comparison of historical records to identify new follows or unfollows.

## Features

*   **Scrape Following/Followers:** Automate the process of collecting a user's following or followers list.
*   **Headless Mode:** Option to run the browser in headless mode for background operation.
*   **Historical Comparison:** Compare current scraped data with previously saved records to detect "added" or "removed" users.
*   **Record Management:** Automatically saves timestamped JSON records of user lists for historical tracking.
*   **Command-Line Interface (CLI):**
    *   Initiate a new tracking session.
    *   Perform quick comparisons between the two most recent records for a user.
    *   Manually select and compare any two historical record files.
    *   Guided setup for browser login.

## Technologies Used

*   **Python:** The core programming language.
*   **Selenium:** For browser automation and interaction with Twitter.
*   **`undetected_chromedriver`:** A patched ChromeDriver that avoids detection by websites like Twitter.
*   **`colorama`:** For enhancing CLI output with colors.
*   **`python-decouple`:** For managing environment variables and configuration.
*   **`pathlib`:** For object-oriented filesystem paths.
*   **`logging`:** For comprehensive application logging.

## Getting Started

### Prerequisites

*   Python 3.x installed.
*   `uv` (or `pip`) for package management.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/twitter-follow-scraper.git
    cd twitter-follow-scraper
    ```

2.  **Install dependencies:**
    ```bash
    uv pip install -r requirements.txt
    # or using pip
    # pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    Copy `config.env.template` to `.env` and configure any necessary environment variables, especially for Twitter selectors if they change.

    ```bash
    cp config.env.template .env
    ```

### Usage

Run the main application:

```bash
python src/main.py
```

The application will present a menu with the following options:

1.  **Run a new tracking scene:** Starts a new scraping process for a specified user's following or followers.
2.  **Compares recent users record:** Compares the two most recent records for a given user.
3.  **File selection from the various list of users records:** Allows manual selection of two record files for comparison.
4.  **Open browser to set up (recommended for first launch):** Launches a browser for manual Twitter login to establish a session.

Follow the on-screen prompts to navigate through the options.


## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
