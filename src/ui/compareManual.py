from pathlib import Path
from textual import on
from textual.widgets import Button, Input, Select

from common.types import MODE
from models.users import UserRecords
from ui.compareQuick import CompareScreen
from ui.recordSelector import FileSelectionScreen


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

        history = UserRecords(self.username, self.mode)
        if not history.path.exists():
            self.notify(f"Error no such records exists at:\n{history.path}", severity="error", timeout=2)
            return

        self.app.switch_screen(FileSelectionScreen(history))
