from pathlib import Path
from textual import on
from textual.app import ComposeResult
from textual.containers import Center
from textual.screen import Screen
from textual.widgets import Button, DirectoryTree, Footer, Header, Label

from models.users import UserRecords
from common.exceptions import FiledecodeError
from ui.recordResult import ResultsScreen


class FileSelectionScreen(Screen):
    def __init__(self, history: UserRecords):
        super().__init__()
        self.history = history
        self.past_path : Path | None = None
        self.future_path : Path | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        # using DirectoryTree is substantially faster than ListView or VerticalScroll
        # figures loading hundreds of records slows too much
        with Center(classes="center-max-elem-100"):
            yield Label("Past Records", id="past-label")
            yield DirectoryTree(self.history.path, id="past-records", classes="my-1")
            yield Label("future Records", id="future-label")
            yield DirectoryTree(self.history.path, id="future-records", classes="my-1")

            yield Button("Continue", id="compare", variant="success", )
            yield Button("Cancel", action="app.go_back", id="back", variant="error")
        yield Footer()

    @on(DirectoryTree.FileSelected, "#past-records")
    def filePastSelect(self, event: DirectoryTree.FileSelected):
        label = self.query_one("#past-label", Label)
        self.past_path = event.path
        label.update(f"Past Records: [magenta]{self.past_path.stem}[/]")

    @on(DirectoryTree.FileSelected, "#future-records")
    def fileFutureSelect(self, event: DirectoryTree.FileSelected):
        label = self.query_one("#future-label", Label)
        self.future_path = event.path
        label.update(f"future Records: [cyan]{self.future_path.stem}[/]")

    @on(Button.Pressed, "#compare")
    def compare(self, event: Button.Pressed):
        if not self.past_path or not self.future_path:
            self.notify("Please select both records!", severity="warning")
            return

        try:
            then_snap = self.history.load_snapshot(self.past_path)
            now_snap = self.history.load_snapshot(self.future_path)

            results = now_snap - then_snap
            self.app.switch_screen(ResultsScreen(results))

        except FiledecodeError as e:
            self.notify(str(e), severity="error")
