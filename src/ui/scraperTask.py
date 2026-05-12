from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Grid
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Checkbox, Label, Select

from common.types import MODE
from ui.scraperProgress import ScraperProgressScreen

class ScraperConfigScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Grid(id="input-grid"):
                yield Label("Run the browser on Headless mode?")
                yield Checkbox("Headless", value=True, id="headless_check")

                yield Label("Which users follow you want to scrape?")
                yield Select(
                    [("Following", MODE.following), ("Followers", MODE.followers)],
                    id="mode_select",
                    value=MODE.following,
                    allow_blank=False
                )

            yield Button("Start Scraping", id="start", variant="primary")
            yield Button("Go Back", id="back", action="app.pop_screen")
        yield Footer()

    @on(Button.Pressed, "#start")
    def start_tasks(self) -> None:
        headless = self.query_one("#headless_check", Checkbox).value
        mode: MODE = self.query_one("#mode_select", Select).value  # pyright: ignore[reportAssignmentType]

        self.app.push_screen(ScraperProgressScreen(headless=headless, mode=mode))
