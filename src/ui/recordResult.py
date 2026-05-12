from colorama import Fore, Style
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Label, Button, Footer, Static
from textual.containers import Center, Vertical

from common.types import ComparisonResults


class ResultsScreen(Screen):
    def __init__(self, results: ComparisonResults):
        super().__init__()
        self.results = results

    def compose(self) -> ComposeResult:
        yield Header()
        with Center(id="results-container"):
            yield Label("Comparison Results", id="title")

            yield Label("Missing Users", id="removed-header")
            removed_list = "\n".join([f"{u} -> {s}" for u, s in self.results.removed.items()])
            yield Static(removed_list if removed_list else "No users removed.", id="removed-list")
            yield Label(f"Total missing: {len(self.results.removed)}", id="removed-total")

            yield Label("Added Users", id="added-header")
            added_list = "\n".join([f"{u}" for u in self.results.added])
            yield Static(added_list if added_list else "No users added.", id="added-list")
            yield Label(f"Total added: {len(self.results.added)}", id="added-total")

            yield Button("Go Back", action="app.back", variant="primary")
        yield Footer()
