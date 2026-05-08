from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header

from ui.scraper import ScraperConfigScreen
from ui.compare import QuickCompareScreen, ManualCompareScreen
from ui.login import BrowserLoginScreen
from config.setup import setup_logging

class TwitterScraperApp(App):
    CSS_PATH = 'styles.tcss'

    def on_mount(self) -> None:
        setup_logging(self)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Button(label="Start scraping", id="task-scrape", variant="primary"),
            Button(label="Quick Comparison", id="task-quick-compare", variant="warning"),
            Button(label="Manual Comparison", id="task-manual-compare", variant="warning"),
            Button(label="Configure Browser/Twitter", id="configure-browser", variant="success"),
            Button(label="Quit", id="quit", variant="error"),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "task-scrape":
            self.push_screen(ScraperConfigScreen())
        elif event.button.id == "task-quick-compare":
            self.push_screen(QuickCompareScreen())
        elif event.button.id == "task-manual-compare":
            self.push_screen(ManualCompareScreen())
        elif event.button.id == "configure-browser":
            self.push_screen(BrowserLoginScreen())
        elif event.button.id == "quit":
            self.exit()


if __name__ == '__main__':
    app = TwitterScraperApp()
    app.run()
