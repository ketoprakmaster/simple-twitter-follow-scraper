# Agents Guide: Twitter Follow Scraper

## Architecture & Tech Stack
- **Core:** Asynchronous Python (`asyncio`) using `nodriver` (CDP) for browser automation.
- **Entry Point:** `src/main.py`
- **Structure:**
    - `src/core/`: Browser driver and scraping logic (`twitterDriver.py`).
    - `src/cli/`: CLI menus and user input handling (`input.py`).
    - `src/common/`: Shared utilities (`utils.py`) and decorators (`decorators.py`).
- **Note:** `README.md` is outdated and mentions Selenium; the project has migrated to `nodriver`.

## Critical Async Constraints
- **No Blocking Calls:** NEVER use `time.sleep()` inside `async def` functions. Use `await asyncio.sleep()`.
- **Await Coroutines:** Ensure all coroutines are properly `await`ed.
- **Async Decorators:** Decorators wrapping `async` functions must be implemented to handle coroutines (see `src/common/decorators.py`).
- **Main Loop:** `src/main.py` uses `inspect.iscoroutinefunction()` to safely call both sync and async CLI functions.

## Developer Commands
- **Run Application:** `uv run src/main.py`
- **Install Dependencies:** `uv sync` or `pip install -r requirements.txt`
- **Testing:** `pytest` (Python path is configured in `pyproject.toml`)

## Configuration
- Environment variables are managed via `python-decouple`.
- Configuration template: `config.env.template` $\rightarrow$ `.env`
