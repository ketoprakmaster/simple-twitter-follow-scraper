from core import *

class USER(enum.Enum):
    EXIST = enum.auto()
    MISSING = enum.auto()
    ADDED = enum.auto()
    BANNED = enum.auto()
    DELETED = enum.auto()

class notEnoughFileToCompare(Exception):
    "when not enough users records is made for comparison"
    
    def __init__(self, records: list[Path]) -> None:
        records = [record.name for record in records]
        self.message:str = f"not enough users records to be made for comparison..\nall user records: {records}"
        super().__init__(self.message)

### python files users class/list handling #####
def save_users_record_to_path(user_path: Path, users_set: set) -> None:
    """ saves the user follow record to the specified user path destination with the datetime as the file names. 

    args:
        user_path (Path, str): an user path ex: "'userhandle'/'follow'" as file destination
        users (set): a user set containing user follows
    """
    filename = time.strftime("%Y.%m.%d") + ".txt"       #   datetime as the filenames
    file_path = Path.cwd() / user_path                  #   the full path of dir
    file_path.mkdir(parents=True,exist_ok=True)         #   ensure the path of dir exists
    with open(file_path / filename ,'w') as file:
        file.write(f"total number of users: ({len(users_set)})\n\n")
        users = sorted(f"{user}\n" for user in users_set)   # converts it to a list and then sort it
        file.writelines(users)
    print(f"user handles saved to : \n{file_path / filename}\n")

def save_accumulated_records(user_path: Path) -> None:
    """save the entire accumalated of user follow record from a given user path 

    args: user_path (Path): an user path ex: "'userhandle'/'follow'" as file destination
    """
    # retrieve all users records from a given user_path.
    # if it fails to vailidate it will return
    try:
        all_records = returns_atleast_two_user_records(user_path=user_path)
    except (FileNotFoundError,notEnoughFileToCompare) as e:
        print(e)
        return
    
    # read the entire user records from beginning (except from the last/newest [-1]) to the end 
    past_users_set = set()
    for record in all_records[:-1]:
        past_users_set.update(read_from_record(record))
    
    # read the newest record from a certain user
    current_users_set = read_from_record(all_records[-1])
    
    users_dict = users_records_comparison(past_users_set,current_users_set)

    with open(Path.cwd() / user_path / "all_user_records.txt",'w')as file:
        # USER.EXIST writes
        file.write(f"total number of users: {len(users_dict[USER.EXIST])}\n\n") 
        users = sorted(f"{user}\n" for user in users_dict[USER.EXIST])
        file.writelines(users)
        
        # USER.MISSING writes
        file.write(f"\n\ntotal number of missing users: {len(users_dict[USER.MISSING])}\n\n") 
        users = sorted(f"{user.ljust(60,'.')} : missing\n" for user in users_dict[USER.MISSING])
        file.writelines(users)
        
    
    print(f"user entire records saved to : \n{Path(user_path) / "all_user_records.txt"}\n")

def users_records_comparison(users_past:set ,users_future: set ) -> dict[USER,set]:
    """
    making a comparison between 2 users records (set).
    
    returns a (dict) containing USER.MISSING, USER.ADDED, AND USERS.EXIST as a set."""
    users = {}

    # check if user record from past records difference to future user record
    # user record from the past that is missing is considered as missing (USER.MISSING)
    users[USER.MISSING] = users_past.difference(users_future)
    
    # check if users record from the future records difference to past user record
    # if a user from future record is missing from the past, that user will be considered added (USER.ADDED)
    users[USER.ADDED] = users_future.difference(users_past)
    
    # add the current users as USERS.EXIST
    users[USER.EXIST] = users_future
    
    return users

def output_users_changes(users: dict) -> None:
    """requires an argument (dict) containing both USER.MISSING and USER.ADDED, then output it onto a terminal"""
    if USER.ADDED not in users or USER.MISSING not in users:
        raise ValueError(f"certain user value does not exist.. \nuser: {users}")
    
    # ouput an user that is missing
    print("\n"+" Missings Users : ".center(70,"="))
    for user in users[USER.MISSING]:
        print(f"{user} is missing!")       
    if not users[USER.MISSING]:
        print("no compared users that are missing..\n")
    else:
        print(f"\ntotal missing users: {len(users[USER.MISSING])}\n")
     
    # ouput an user that is added
    print(" Added Users : ".center(70,"=")) 
    for user in users[USER.ADDED]:
        print(f"{user} is added!")

    if not users[USER.ADDED]:
        print("no compared users that are added..\n")
    else:
        print(f"\ntotal added users: {len(users[USER.ADDED])}\n")


def read_from_recent_user_records(user_path:str) -> set[str]:
    """given a user path (str) which contains a users records history.
    returns a (set) of user follow from the newest record
    
    Raises an exception if the specified directory of folders/file does not exist"""
    
    record = return_all_records(user_path)
    
    return read_from_record(record[-1])

def read_from_record(full_path:Path) -> set[str]:
    """input the full path of an user record in order to read it successfully, returns a set"""
    # print(f"reading user record from: {full_path}")
    
    users = full_path.read_text()
    users = {line.lower() for line in users.split("\n") if "@" in line}
    
    return users

def returns_atleast_two_user_records(user_path:str) -> list[Path]:
    """return a valid users records (list[Path]) necessary for two seperate user records for comparison.
    
    raises an exception if not enough (atleast 2) user follow record that is needed to make a comparison"""
    # retrieve all users records from a given user_path
    all_records = return_all_records(path=user_path)
    
    if len(all_records) <= 1:
        raise notEnoughFileToCompare(all_records)
    
    return all_records
   
def return_all_records(path:str) -> list[Path]:
    """given a user path it will return a list of user records with an full path to each.
    Raises an exception if the specified directory of folders/file does not exist"""
    path = Path.cwd() / path
    
    if not path.exists():
        raise FileNotFoundError(f"invalid.. no directory exists\ndirectory  in question: {path}\n")
    
    allRecords = []
    for file in path.glob("*.txt"):
        if "all" not in file.name:
            allRecords.append(file)
    
    return allRecords
