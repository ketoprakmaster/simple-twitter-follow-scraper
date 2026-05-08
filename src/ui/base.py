from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header

class BaseScreen(Screen):
    BINDINGS = [
        ("q", "app.pop_screen", "Go Back"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
    ]
