from textual.app import ComposeResult
from textual.containers import Center
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label
from core.twitterDriver import TwitterDriver

class BrowserLoginScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Center(classes="center-max-elem-100 mt-2"):
            yield Label("Please log in to Twitter in the opened browser window.", classes="mt-2")
            yield Label("Once you are logged in and on the home page, click the button below.", classes="mb-2")
            yield Button("I have logged in", action="app.go_back", variant="success")
        yield Footer()

    def on_mount(self) -> None:
        self.driver = TwitterDriver(headless=False)
        self.run_worker(self.init_driver(), thread=False)

    async def init_driver(self):
        try:
            await self.driver.initialize_driver()
        except Exception as e:
            self.query_one(Label).update(f"Error initializing browser: {e}")

    def on_unmount(self) -> None:
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
