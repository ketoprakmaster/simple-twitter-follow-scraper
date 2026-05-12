from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Label, Button, Footer

from common.types import ComparisonResults


class ResultsScreen(Screen):
    def __init__(self, results: ComparisonResults):
        super().__init__()
        self.results = results

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Comparison Results", id="title")

        removed_list = "\n".join([f"{u} -> {s}" for u, s in self.results.removed.items()])
        yield Label(f"Removed:\n{removed_list if removed_list else 'None'}", id="removed_label")

        added_list = "\n".join([f"{u}" for u in self.results.added])
        yield Label(f"Added:\n{added_list if added_list else 'None'}", id="added_label")

        yield Button("Return to Menu", action="app.back", variant="primary")
        yield Footer()
