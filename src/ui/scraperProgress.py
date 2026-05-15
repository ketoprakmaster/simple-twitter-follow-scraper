from textual.app import ComposeResult
from textual.containers import Center
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, RichLog

from common.types import MODE
from scraper.pipeline import ScraperPipeline
from ui.recordResult import ResultsScreen


class ScraperProgressScreen(Screen):
    def __init__(self, headless: bool, mode: MODE):
        super().__init__()
        self.headless = headless
        self.mode = mode

    def compose(self) -> ComposeResult:
        yield Header()
        with Center(classes="center-max-elem-100"):
            yield Label("Scraping in progress... please wait.", classes="text-center")
            yield RichLog(id="main_log", markup=True, classes="my-2")
            yield Button("Cancel", action="app.go_back", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self.app.active_rich_log = self.query_one("#main_log")  # pyright: ignore
        self.scrape_worker = self.run_worker(self.do_scrape(), thread=False)

    async def do_scrape(self):
        scraper = None
        try:
            pipeline = ScraperPipeline(self.headless, self.mode)

            await pipeline.initialize()
            results = await pipeline.run()

            self.app.switch_screen(ResultsScreen(results=results))

        except Exception as e:
            self.query_one("#main_log", RichLog).write(f"[red]Error: {e}[/red]")
        finally:
            if scraper:
                scraper.quit()

    def _on_unmount(self) -> None:
        self.app.active_rich_log = None   # pyright: ignore
        self.scrape_worker.cancel()
        return super()._on_unmount()
