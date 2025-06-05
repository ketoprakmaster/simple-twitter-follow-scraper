from pathlib import Path
import time
import enum
import os
import json
import random
#import logging

class UserScrapeOperationFailed(Exception):
    "general catch all term for when failing scraping users follows"

class NotEnoughUserRecords(Exception):
    "ensure to have atleast two user follow records for comparison"
    
class FiledecodeError(Exception):
    "failed to decode json objects"

def clear():
    os.system("cls")

