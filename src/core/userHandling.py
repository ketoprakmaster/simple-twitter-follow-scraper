from core import *

# set the user log
userLog = logging.getLogger("users")

### python files users class/list handling #####
def read_from_record(fullPath:Path) -> set[str]:
    """input the full path of an user record in order to read it successfully, returns a set"""
    try:
        with open(fullPath,"r") as obj:
            users = json.load(obj)["users"]
    except json.JSONDecodeError:
        raise FiledecodeError(f"failed to decode json path:{fullPath}")
    return set(users)

   
def return_all_records(username : str, mode : MODE) -> list[Path]:
    """given a user path it will return a list of user records with an full path to each.
    Raises an exception if the specified directory of folders/file does not exist"""
    path : Path = USER_RECORDS / username / mode
    
    if not path.exists():
        raise FileNotFoundError(f"invalid.. no directory exists, directory  in question: {path=}")
    
    allRecords = []
    for file in path.glob("*"):
        if "all" in file.name:
            continue
        allRecords.append(file)
    
    return allRecords


def read_from_recent_user_records(username: str, mode: MODE) -> set[str]:
    """given a user path (str) which contains a users records history.
    returns a (set) of user follow from the newest record
    
    Raises an exception if the specified directory of folders/file does not exist"""
    
    record = return_all_records(username, mode)
    
    return read_from_record(record[-1])


def save_users_record_to_path(username: str, mode: MODE, users_set: set) -> None:
    """ saves the user follow record to the specified user path destination with the datetime as the file names. 

    args:
        username (str): as user name for "'userhandle'/'follow'" as file destination
        mode (MODE): which user records to save (either following or followers)
        users (set): a user set containing user follows
    """
    filename = time.strftime("%Y.%m.%d") + ".json"          #   datetime as the filenames
    file_path = USER_RECORDS / username / mode              #   the full path of dir
    file_path.mkdir(parents=True,exist_ok=True)             #   ensure the path of dir exists
    with open(file_path / filename ,'w') as file:
        obj = {"total_follows": len(users_set),"users":sorted(users_set)}
        json.dump(obj,file,indent=4)
    logging.info(f"user handles saved to : {file_path}")


def makeComparison(users_past:set ,users_future: set ) -> comparisonResults:
    """
    making a comparison between 2 users records (set).
    
    returns a object (comparisonResults) as a set."""
    # check if user record from past records difference to future user record
    # user record from the past that is missing is considered as missing
    missings = users_past.difference(users_future)
    # check if users record from the future records difference to past user record
    # if a user from future record is missing from the past, that user will be considered added
    added = users_future.difference(users_past)

    return comparisonResults(removed=missings,added=added)


def compare_recent_records(username: str, mode: MODE) -> comparisonResults:
    "check existing saved user record if sufficient records exists (atleast 2)" 
    all_records = return_all_records(username, mode)
    
    if len(all_records) < 2:
       raise NotEnoughUserRecords(f"Not enough user records for comparison. {all_records=}")

    past_user_list = read_from_record(all_records[-2])
    current_user_list = read_from_record(all_records[-1])
    
    # log the fetch records
    userLog.info(f"past record: {all_records[-2]}")
    userLog.info(f"current record: {all_records[-1]}")
    
    results = makeComparison(past_user_list,current_user_list)
    
    return results