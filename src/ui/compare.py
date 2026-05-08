from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, Button, Input, Select, RichLog, Label, ListView, ListItem
from pathlib import Path

from common.types import MODE
from ui.base import BaseScreen
from core.userHandling import UserSnapshot
from common.exceptions import (
    NotEnoughUserRecords,
    FiledecodeError,
    UserRecordsNotExists,
)
from ui.scraper import ResultsScreen

class QuickCompareScreen(BaseScreen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Label("Enter Twitter Username:"),
            Input(placeholder="@username", id="user_input"),
            Select([(m.value, m) for m in MODE], id="mode_select", value=MODE.following),
            Button("Compare", variant="primary", id="compare_btn"),
            Button("Go Back", id="back_btn"),
            RichLog(id="main_log"),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_btn":
            self.app.pop_screen()
            return

        if event.button.id == "compare_btn":
            username = self.query_one("#user_input", Input).value
            mode = self.query_one("#mode_select", Select).value
            log = self.query_one("#main_log", RichLog)

            try:
                temp = UserSnapshot(username, mode, set())
                all_records = sorted(temp._return_all_stored_records())

                if len(all_records) < 2:
                    raise NotEnoughUserRecords("Need at least 2 records for a quick comparison.")

                latest_users = temp._read_from_single_records(all_records[-1])
                past_users = temp._read_from_single_records(all_records[-2])

                now_snap = UserSnapshot(username, mode, latest_users, timestamp=all_records[-1].stem)
                then_snap = UserSnapshot(username, mode, past_users, timestamp=all_records[-2].stem)

                results = now_snap - then_snap
                self.app.push_screen(ResultsScreen(results=results))

            except (NotEnoughUserRecords, UserRecordsNotExists, FiledecodeError) as e:
                log.write(f"[red]{e}[/red]")

class ManualCompareScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.username = ""
        self.mode = MODE.following
        self.past_path = None
        self.future_path = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Label("Enter Twitter Username:"),
            Input(placeholder="@username", id="user_input"),
            Select([(m.value, m) for m in MODE], id="mode_select", value=MODE.following),
            Button("Select Files", variant="primary", id="select_files"),
            Button("Go Back", id="back"),
            RichLog(id="main_log", markup=True),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
            return

        if event.button.id == "select_files":
            self.username = self.query_one("#user_input", Input).value
            self.mode = self.query_one("#mode_select", Select).value

            if not self.username:
                self.query_one("#main_log", RichLog).write("[red]Please enter a username[/red]")
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

class FileSelectionScreen(BaseScreen):
    def __init__(self, username, mode, prompt, callback):
        super().__init__()
        self.username = username
        self.mode = mode
        self.prompt = prompt
        self.callback = callback

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(self.prompt)
        yield ListView(id="file_list")
        yield Button("Cancel", id="cancel")
        yield Footer()

    def on_mount(self) -> None:
        temp = UserSnapshot(self.username, self.mode, set())
        files = sorted(temp._return_all_stored_records())
        list_view = self.query_one("#file_list", ListView)
        for f in files:
            list_view.append(ListItem(Label(f.name), id=str(f)))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        # event.item is the ListItem
        file_path = Path(event.item.id)
        self.callback(file_path)
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
