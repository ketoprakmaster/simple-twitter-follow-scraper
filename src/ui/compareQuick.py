from textual import on
from textual.app import ComposeResult
from textual.containers import Center
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Input, Select, Label

from common.types import MODE
from core.userHandling import UserSnapshot
from common.exceptions import (
    NotEnoughUserRecords,
    FiledecodeError,
    UserRecordsNotExists,
)
from ui.recordResult import ResultsScreen

class QuickCompareScreen(Screen):
    BINDINGS = [('ctrl+c', 'screen.compare', 'continue')]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Center(
            Label("Enter Twitter Username:"),
            Input(placeholder="@username", id="user_input"),
            Select([(m.value, m) for m in MODE], id="mode_select", allow_blank=False),
            Button("Compare", variant="primary", id="compare_btn"),
            Button("Go Back", action="app.back"),
        )
        yield Footer()

    @on(Button.Pressed, "#compare_btn")
    def action_compare(self) -> None:
        username = self.query_one("#user_input", Input).value
        mode : MODE = self.query_one("#mode_select", Select).value  # pyright: ignore[reportAssignmentType]

        if not username or mode not in MODE:
            self.notify("Please fill the corresponding Input!", severity="warning", timeout=1)
            return

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
            self.notify(f"ERROR: {e}", severity="error",timeout=1)
