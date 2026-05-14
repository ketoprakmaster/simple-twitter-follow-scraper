from pathlib import Path
from textual import on, work
from textual.widgets import Button, Input, RichLog, Select

from common.types import MODE
from core.userHandling import UserSnapshot
from config.paths import USER_RECORDS_DIR
from ui.compareQuick import CompareScreen
from ui.recordSelector import FileSelectionScreen
from ui.recordResult import ResultsScreen

# TODO: wip
class ManualCompareScreen(CompareScreen):
    def __init__(self):
        super().__init__()
        self.username = ""
        self.mode = MODE.following
        self.past_path : Path | None = None
        self.future_path = None

    @on(Button.Pressed, "#compare_btn")
    def continue_btn(self, event: Button.Pressed) -> None:
        self.username = self.query_one("#user_input", Input).value
        self.mode: MODE = self.query_one("#mode_select", Select).value  # pyright: ignore

        if self.mode not in MODE or not self.username:
            self.notify("Please fill the corresponding Input!", severity="warning", timeout=2)
            return

        user_dir = USER_RECORDS_DIR / self.username / self.mode
        if not Path(user_dir).exists():
            self.notify(f"Error no such records exists at:\n{user_dir}", severity="error", timeout=2)
            return

        self.app.switch_screen(FileSelectionScreen(self.username,self.mode))
