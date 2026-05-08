from textual.app import ComposeResult
from textual.widgets import Button, Footer, Header, Label
from ui.base import BaseScreen
from core.twitterDriver import TwitterDriver

class BrowserLoginScreen(BaseScreen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Please log in to Twitter in the opened browser window.")
        yield Label("Once you are logged in and on the home page, click the button below.")
        yield Button("I have logged in", id="done", variant="success")
        yield Button("Cancel", id="cancel")
        yield Footer()

    def on_mount(self) -> None:
        # Launch browser in non-headless mode
        self.driver = TwitterDriver(headless=False)
        self.run_worker(self.init_driver(), thread=False)

    async def init_driver(self):
        try:
            await self.driver.initialize_driver()
        except Exception as e:
            self.query_one(Label).update(f"Error initializing browser: {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "done":
            if self.driver:
                self.driver.quit()
            self.app.pop_screen()
        elif event.button.id == "cancel":
            if self.driver:
                self.driver.quit()
            self.app.pop_screen()

    def on_unmount(self) -> None:
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
