from pathlib import Path
from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Grid, Horizontal, HorizontalGroup, Vertical
from textual.screen import Screen
from textual.widgets import Button, DirectoryTree, Footer, Header, Label, ListItem, ListView

from core.userHandling import UserSnapshot
from config.paths import USER_RECORDS_DIR
from ui.recordResult import ResultsScreen


class FileSelectionScreen(Screen):
    def __init__(self, username, mode):
        super().__init__()
        self.username = username
        self.mode = mode
        self.path = USER_RECORDS_DIR / username / mode

    def compose(self) -> ComposeResult:
        yield Header()
        with Center(classes="center-max-elem-100"):
            yield Label("Past Records", id="past-label")
            yield DirectoryTree(self.path, id="past-records", classes="my-1")
            yield Label("future Records", id="future-label")
            yield DirectoryTree(self.path, id="future-records", classes="my-1")

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
        if hasattr(self, "past_path") and hasattr(self, "future_path"):
            temp = UserSnapshot(self.username, self.mode, set())

            latest_users = temp._read_from_single_records(self.future_path)
            past_users = temp._read_from_single_records(self.past_path)

            now_snap = UserSnapshot(self.username, self.mode, latest_users)
            then_snap = UserSnapshot(self.username, self.mode, past_users)

            results = now_snap - then_snap
            self.app.switch_screen(ResultsScreen(results))
        else:
            self.notify("Please fill the corresponding Input!", severity="warning", timeout=1)
