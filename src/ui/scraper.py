from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Checkbox, Label, Select, RichLog
from textual.worker import Worker, WorkerState

from common.types import MODE
from ui.base import BaseScreen
from core.twitterDriver import TwitterDriver
from core.userHandling import UserSnapshot
from common.exceptions import UserScrapeOperationFailed, DriverNotInitialized

class ScraperConfigScreen(BaseScreen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Label(content="Run the browser on Headless mode?"),
            Checkbox("Headless", value=True, id="headless_check"),
            Label(content="Which users follow you want to scrape?"),
            Select([("Following", MODE.following), ("Followers", MODE.followers)], id="mode_select", value=MODE.following),
            Button("Start Scraping", id="start", variant="primary"),
            Button("Go Back", id="back"),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "start":
            headless = self.query_one("#headless_check", Checkbox).value
            mode = self.query_one("#mode_select", Select).value
            self.app.push_screen(ScraperProgressScreen(headless=headless, mode=mode))

class ScraperProgressScreen(BaseScreen):
    def __init__(self, headless: bool, mode: MODE):
        super().__init__()
        self.headless = headless
        self.mode = mode

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Scraping in progress... please wait.", id="status_label")
        yield RichLog(id="main_log", highlight=True, markup=True)
        yield Button("Cancel", id="cancel", variant="error")
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.scrape_worker.cancel()
            self.app.pop_screen()

class ResultsScreen(BaseScreen):
    def __init__(self, results):
        super().__init__()
        self.results = results

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Comparison Results", id="title")

        removed_list = "\n".join([f"{u} -> {s}" for u, s in self.results.removed.items()])
        yield Label(f"Removed:\n{removed_list if removed_list else 'None'}", id="removed_label")

        added_list = "\n".join([f"{u}" for u in self.results.added])
        yield Label(f"Added:\n{added_list if added_list else 'None'}", id="added_label")

        yield Button("Return to Menu", id="back", variant="primary")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
