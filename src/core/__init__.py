from pathlib import Path
from dataclasses import dataclass, field
import time
import enum
import os
import json
import random
import logging

class UserScrapeOperationFailed(Exception):
    "general catch all term for when failing scraping users follows"

class NotEnoughUserRecords(Exception):
    "ensure to have atleast two user follow records for comparison"
    
class FiledecodeError(Exception):
    "failed to decode json objects"

class UserRecordsNotExists(Exception):
    "no users records exist"

def clear():
    """flushing the cli"""
    os.system("cls")

def pause(msg: str = "\npress to continue.."):
    """pausing until any key presses"""
    input()

class MODE(enum.StrEnum):
    following = "following"
    followers = "followers" 

# set the logger
# set the file handlers
filelog = logging.FileHandler(filename="logging.log")
fileFormatter = logging.Formatter("%(name)-10s: %(asctime)s - %(levelname)-8s -  %(filename)s:%(lineno)s  >>> %(message)s")
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


# struct for records comparison
@dataclass(frozen=True)
class comparisonResults():
    removed: set[str] = field(default_factory=set)
    added: set[str] = field(default_factory=set)
    
# set global variables:
USER_PROFILE_DIR = Path.cwd() / "profile"
USER_RECORDS_DIR = Path.cwd() / "records"

if USER_PROFILE_DIR.exists:
    logging.info(f"current users profile : {USER_PROFILE_DIR}")
else:
    logging.warning("no users profile detected, it will generated a new one instead")
