import json
import logging
import time
from pathlib import Path

from config.paths import USER_RECORDS_DIR
from common.types import MODE, ComparisonResults, UserStatus
from common.exceptions import UserRecordsNotExists, NotEnoughUserRecords, FiledecodeError
from common.decorators import timing_decorator

userLog = logging.getLogger("users")

class UserSnapshot:
    def __init__(self, username: str, mode: MODE, users: set[str], timestamp: str | None = None):
        self.username = username
        self.mode = mode
        self.users = users # Always expect a set here
        self.timestamp = timestamp or time.strftime("%Y.%m.%d %H.%M.%S")

    @classmethod
    def from_latest(cls, username: str, mode: MODE):
        """Factory method: finds the latest file and returns a UserSnapshot instance."""
        instance = cls(username, mode, users=set()) # Temporary shell
        all_records = instance._return_all_stored_records()

        # Sort by filename to ensure chronological order
        latest_path = sorted(all_records)[-1]

        userLog.info(f"Loading latest record: {latest_path.name}")
        users = instance._read_from_single_records(latest_path)

        # Return a fully formed object
        return cls(username, mode, users, timestamp=latest_path.stem)

    @timing_decorator("saving users records")
    def save(self):
        """Saves the current instance's user set to disk."""
        file_path = USER_RECORDS_DIR / self.username / self.mode
        file_path.mkdir(parents=True, exist_ok=True)

        filename = f"{self.timestamp}.json"
        full_path = file_path / filename

        with open(full_path, 'w') as file:
            # Use self.users directly from the object
            json.dump({"users": sorted(list(self.users))}, file, indent=4)

        userLog.info(f"Snapshot saved to: {full_path}")

    def __sub__(self, other: "UserSnapshot") -> ComparisonResults:
        """The 'Magic': NewSnapshot - OldSnapshot"""
        if not isinstance(other, UserSnapshot):
            raise TypeError("Can only subtract UserSnapshot objects")

        removed = {u: UserStatus.MISSING for u in other.users if u not in self.users}
        added = {u for u in self.users if u not in other.users}
        return ComparisonResults(removed=removed, added=added)

    def _return_all_stored_records(self, user_path: Path | None = None):
        """either give a user path whole or use predefined object class var, it will return a list of user records with an full path to each.
        Raises an exception if the specified directory of folders/file does not exist"""
        if not user_path:
            user_path = USER_RECORDS_DIR / self.username / self.mode

        if not user_path.exists():
            userLog.error(f"invalid directory, doesn't exist: {user_path}")
            raise UserRecordsNotExists(f"invalid.. no directory exists, directory in question: {user_path=}")

        allRecords = []
        for file in user_path.glob("*"):
            if "all" in file.name:
                continue
            allRecords.append(file)

        if not allRecords:
            userLog.error(f"no users records exists : {user_path}")
            raise UserRecordsNotExists(f"no user records exists in : {user_path}")

        return allRecords

    def _read_from_single_records(self, fullPath: Path):
        """input the full path of an user record in order to read it successfully, returns a set"""
        try:
            with open(fullPath,"r") as obj:
                users : list[str] = json.load(obj)["users"]
        except (json.JSONDecodeError, KeyError) as e:
            userLog.error(f"failed to decode json path: {fullPath} error:{e}")
            raise FiledecodeError(f"failed to decode json path:{fullPath}")

        return set(users)
