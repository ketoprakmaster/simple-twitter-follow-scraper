from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Label, Button, Static
from textual.containers import Horizontal, Vertical, VerticalScroll

from common.types import ComparisonResults

class ResultsScreen(Screen):
    BINDINGS = [("escape", "app.go_back", "Back")]

    def __init__(self, results: ComparisonResults):
        super().__init__()
        self.results = results

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Comparison Results", classes="w-full text-center my-1")
        with Horizontal():
            with Vertical(classes="bg-lighten-1 m-1 p-1 border-primary"):
                yield Label(f"Missing Users ({len(self.results.removed)})", classes="mb-1")
                removed_items = [
                    Static(f"{u:<20} is [red]({s})[/]")
                    for u, s in self.results.removed.items()
                ]
                yield VerticalScroll(*removed_items) if removed_items else Label("No users removed.")
            with Vertical(classes="bg-lighten-1 m-1 p-1 border-primary"):
                yield Label(f"Added Users ({len(self.results.added)})", classes="mb-1")
                added_items = [
                    Static(f"{u:<20} is [green]added[/]")
                    for u in self.results.added
                ]
                yield VerticalScroll(*added_items) if added_items else Label("No users added.")

        yield Button("Go Back", id="back-btn", variant="primary", classes="m-1 w-full")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back-btn":
            self.app.pop_screen()
