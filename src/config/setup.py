import logging
import threading
from rich.markup import escape
from textual.widgets import RichLog

from config.paths import LOG_FILE_PATH

class TextualHandler(logging.Handler):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._main_thread_id = threading.get_ident()

    def emit(self, record):
        try:
            level = record.levelname
            message = escape(record.getMessage())
            formatted_msg = f"[bold blue]{level:8}[/] {message}"

            def log_to_active_screen():
                logs = self.app.screen.query("#main_log")
                if not logs:
                    logs = self.app.query("#main_log")

                for log in logs:
                    if isinstance(log, RichLog):
                        log.write(formatted_msg)

            if threading.get_ident() == self._main_thread_id:
                log_to_active_screen()
            else:
                self.app.call_from_thread(log_to_active_screen)

        except Exception:
            self.handleError(record)

def setup_logging(app):
    rootLogger = logging.getLogger()
    rootLogger.handlers = [] # Clear any defaults
    rootLogger.setLevel(logging.INFO)

    # 1. File Handler
    LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True) # ensure dir exists
    filelog = logging.FileHandler(LOG_FILE_PATH.resolve())
    fileFormatter = logging.Formatter(
        "%(name)-10s: %(asctime)s - %(levelname)-8s -  %(filename)s:%(lineno)s   >>> %(message)s"
    )
    filelog.setFormatter(fileFormatter)
    rootLogger.addHandler(filelog)

    # 2. Textual Handler
    textual_handler = TextualHandler(app)
    rootLogger.addHandler(textual_handler)
