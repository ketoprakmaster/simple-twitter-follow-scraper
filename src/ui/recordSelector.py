from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, ListItem, ListView

from core.userHandling import UserSnapshot

# TODO: wip
class FileSelectionScreen(Screen):
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
