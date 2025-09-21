import json
import logging
import time
from pathlib import Path

from core.types import MODE, ComparisonResults
from core.exceptions import UserRecordsNotExists, NotEnoughUserRecords, FiledecodeError 
from core.config import USER_RECORDS_DIR
from core.utils import timing_decorator

userLog = logging.getLogger("users")


def readFromRecords(fullPath:Path) -> set[str]:
    """input the full path of an user record in order to read it successfully, returns a set"""
    try:
        with open(fullPath,"r") as obj:
            users = json.load(obj)["users"]
    except json.JSONDecodeError:
        userLog.error(f"failed to decode json path: {fullPath}")
        raise FiledecodeError(f"failed to decode json path:{fullPath}")
    return set(users)

   
def returnAllRecords(username : str = None, mode : MODE = None, path: Path = None) -> list[Path]:
    """either give a user path whole or separately, it will return a list of user records with an full path to each.
    Raises an exception if the specified directory of folders/file does not exist"""
    if not path:
        path : Path = USER_RECORDS_DIR / username / mode
    
    if not path.exists():
        userLog.error(f"invalid directory, doesn't exist: {path}")
        raise UserRecordsNotExists(f"invalid.. no directory exists, directory  in question: {path=}")
    
    allRecords = []
    for file in path.glob("*"):
        if "all" in file.name:
            continue
        allRecords.append(file)
    
    if not allRecords:
        userLog.error(f"no users records exists : {path}")
        raise UserRecordsNotExists(f"no user records exists in : {path}")
    
    return allRecords


def getUsersRecentRecords(username: str, mode: MODE) -> set[str]:
    """given a user path (str) which contains a users records history.
    returns a (set) of user follow from the newest record
    
    Raises an exception if the specified directory of folders/file does not exist"""
    
    record = returnAllRecords(username, mode)
    userLog.info(f"current_records {record[-1]}")
    
    return readFromRecords(record[-1])

@timing_decorator("saving users records")
def saveUsersRecord(username: str, mode: MODE, users_set: set) -> None:
    """ saves the user follow record to the specified user path destination with the datetime as the file names. 

    args:
        username (str): as user name for "'userhandle'/'follow'" as file destination
        mode (MODE): which user records to save (either following or followers)
        users (set): a user set containing user follows
    """
    filename = time.strftime("%Y.%m.%d %H.%M.%S") + ".json"          #   datetime as the filenames
    file_path = USER_RECORDS_DIR / username / mode              #   the full path of dir
    file_path.mkdir(parents=True,exist_ok=True)             #   ensure the path of dir exists
    with open(file_path / filename ,'w') as file:
        obj = {"users":sorted(users_set)}
        json.dump(obj,file,indent=4)
    userLog.info(f"user handles saved to : {file_path}")


def makeComparison(users_past:set ,users_future: set ) -> ComparisonResults:
    """
    making a comparison between 2 users records (set).
    
    returns a object (ComparisonResults) as a set."""
    # check if user record from past records difference to future user record
    # user record from the past that is missing is considered as missing
    missings = users_past.difference(users_future)
    # check if users record from the future records difference to past user record
    # if a user from future record is missing from the past, that user will be considered added
    added = users_future.difference(users_past)

    return ComparisonResults(removed=missings,added=added)


def compareRecentRecords(username: str, mode: MODE) -> ComparisonResults:
    """check existing saved user record if sufficient records exists (atleast 2)
    
    raises an exception (NotEnoughUserRecords) if it lacks sufficient records
    and (UserRecordsNotExists) if its invalid""" 

    allRecords = returnAllRecords(username, mode)
    
    if len(allRecords) < 2:
        userLog.warning(f"not enough users record for comparison. {allRecords=}")
        raise NotEnoughUserRecords(f"Not enough user records for comparison. {allRecords=}")

    past_user_list = readFromRecords(allRecords[-2])
    current_user_list = readFromRecords(allRecords[-1])
    
    # log the fetch records
    userLog.info(f"past record: {allRecords[-2]}")
    userLog.info(f"current record: {allRecords[-1]}")
    
    results = makeComparison(past_user_list,current_user_list)
    
    return results

def process_new_scrape_results(username: str, mode: MODE, new_users: set) -> ComparisonResults:
    """
    Compares a new set of users against the most recent record.
    Saves the new set if changes are detected.

    Returns the comparison results.
    """
    try:
        past_users = getUsersRecentRecords(username=username, mode=mode)
    except (UserRecordsNotExists, FiledecodeError):
        # If no previous valid record, all new users are "added"
        saveUsersRecord(username=username, mode=mode, users_set=new_users)
        return ComparisonResults(added=new_users)

    # Perform the comparison
    results = makeComparison(users_past=past_users, users_future=new_users)

    # Save only if there are changes
    if results.added or results.removed:
        saveUsersRecord(username=username, mode=mode, users_set=new_users)

    return results