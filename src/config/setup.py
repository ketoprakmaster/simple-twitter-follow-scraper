import logging
import threading
from rich.markup import escape
from textual.app import App

from config.paths import LOG_FILE_PATH

class TextualHandler(logging.Handler):
    def __init__(self, app):
        super().__init__()
        self.app : App = app
        self._main_thread_id = threading.get_ident()

    def emit(self, record):
        try:
            message = record.getMessage()

            def log_to_ui():
                log_widget = getattr(self.app, "active_rich_log", None)
                if log_widget:
                    log_widget.write(message)

            if threading.get_ident() == self._main_thread_id:
                log_to_ui()
            else:
                self.app.call_from_thread(log_to_ui)

        except Exception:
            self.handleError(record)

def setup_logging(app):
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)

    filelog = logging.FileHandler(LOG_FILE_PATH.resolve())
    fileFormatter = logging.Formatter("%(name)-10s: %(asctime)s - %(levelname)-8s -  %(filename)s:%(lineno)s  >>> %(message)s")
    filelog.setFormatter(fileFormatter)
    rootLogger.addHandler(filelog)

    ui_logger = logging.getLogger("ui_status")
    ui_logger.propagate = False

    textual_handler = TextualHandler(app)
    ui_logger.addHandler(textual_handler)
    rootLogger.addHandler(textual_handler)
