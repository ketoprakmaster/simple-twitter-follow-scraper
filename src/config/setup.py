from config.paths import LOG_FILE_PATH

import logging


def setup_logging():
    """Configures the root logger for the application."""
    # set the file handlers
    filelog = logging.FileHandler(filename=LOG_FILE_PATH)
    fileFormatter = logging.Formatter(
        "%(name)-10s: %(asctime)s - %(levelname)-8s -  %(filename)s:%(lineno)s   >>> %(message)s"
    )
    filelog.setFormatter(fileFormatter)

    # set the stream handler
    stdout = logging.StreamHandler()
    consoleFormatter = logging.Formatter("[%(levelname)s] %(message)s ")
    stdout.setFormatter(consoleFormatter)

    # add the handlers to the root loggers
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)
    rootLogger.addHandler(stdout)
    rootLogger.addHandler(filelog)
