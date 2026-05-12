from pathlib import Path
from textual import on
from textual.app import ComposeResult
from textual.containers import Center
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, RichLog, Select

from common.types import MODE
from core.userHandling import UserSnapshot
from ui.recordSelector import FileSelectionScreen
from ui.recordResult import ResultsScreen

# TODO: wip
class ManualCompareScreen(Screen):
    def __init__(self):
        super().__init__()
        self.username = ""
        self.mode = MODE.following
        self.past_path = None
        self.future_path = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Center(
            Label("Enter Twitter Username:"),
            Input(placeholder="@username", id="user_input"),
            Select([(m.value, m) for m in MODE], id="mode_select", allow_blank=False),
            Button("Select Files", variant="primary", id="select_files"),
            Button("Go Back", action="app.back"),
        )
        yield Footer()

    @on(Button.Pressed, "#select_files")
    def continue_btn(self, event: Button.Pressed) -> None:
        self.username = self.query_one("#user_input", Input).value
        self.mode: MODE = self.query_one("#mode_select", Select).value  # pyright: ignore[reportAttributeAccessIssue]

        if self.mode not in MODE or not self.username:
            self.notify("Please fill the corresponding Input!", severity="warning", timeout=2)
            return


        self.app.push_screen(FileSelectionScreen(
            username=self.username,
            mode=self.mode,
            prompt="Select the PAST record file",
            callback=self.on_past_selected
        ))

    def on_past_selected(self, path: Path):
        self.past_path = path
        self.app.push_screen(FileSelectionScreen(
            username=self.username,
            mode=self.mode,
            prompt="Select the FUTURE record file",
            callback=self.on_future_selected
        ))

    def on_future_selected(self, path: Path):
        self.future_path = path
        self.do_compare()

    def do_compare(self):
        try:
            temp = UserSnapshot(self.username, self.mode, set())
            past_snap = UserSnapshot(
                self.username, self.mode, temp._read_from_single_records(self.past_path), timestamp=self.past_path.stem
            )
            future_snap = UserSnapshot(
                self.username, self.mode, temp._read_from_single_records(self.future_path), timestamp=self.future_path.stem
            )
            results = future_snap - past_snap
            self.app.push_screen(ResultsScreen(results=results))
        except Exception as e:
            self.query_one("#main_log", RichLog).write(f"[red]Comparison failed: {e}[/red]")
