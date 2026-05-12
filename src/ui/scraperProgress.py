from textual.app import ComposeResult
from textual.containers import Center
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, RichLog

from common.exceptions import DriverNotInitialized, UserScrapeOperationFailed
from common.types import MODE
from core.twitterDriver import TwitterDriver
from core.userHandling import UserSnapshot
from ui.recordResult import ResultsScreen


class ScraperProgressScreen(Screen):
    def __init__(self, headless: bool, mode: MODE):
        super().__init__()
        self.headless = headless
        self.mode = mode

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            yield Label("Scraping in progress... please wait.", id="status_label")
            yield RichLog(id="main_log", highlight=True, markup=True)
            yield Button("Cancel", action="app.back", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self.scrape_worker = self.run_worker(self.do_scrape(), thread=False)

    async def do_scrape(self):
        scraper = None
        try:
            scraper = TwitterDriver(headless=self.headless, mode=self.mode)
            await scraper.initialize_driver()
            scraped_users = await scraper.scrape_user_follows()
            username = scraper.username

            current_snap = UserSnapshot(username, self.mode, scraped_users)

            try:
                past_snap = UserSnapshot.from_latest(username, self.mode)
                results = current_snap - past_snap
            except Exception: # UserRecordsNotExists
                from common.types import ComparisonResults
                results = ComparisonResults(added=scraped_users)

            if results.removed:
                await results.check_status(driver=scraper)
                false_negatives = {
                    user for user, status in results.removed.items()
                    if status in {"Exists", "Withheld"} # Valid statuses
                }
                if false_negatives:
                    current_snap.users.update(false_negatives)
                    for user in false_negatives:
                        del results.removed[user]

            current_snap.save()
            self.app.push_screen(ResultsScreen(results=results))

        except (UserScrapeOperationFailed, DriverNotInitialized) as e:
            self.query_one("#main_log", RichLog).write(f"[red]Error: {e}[/red]")
        except Exception as e:
            self.query_one("#main_log", RichLog).write(f"[red]Unexpected Error: {e}[/red]")
        finally:
            if scraper:
                scraper.quit()

    def _on_unmount(self) -> None:
        self.scrape_worker.cancel()
        return super()._on_unmount()
