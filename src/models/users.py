import json
import logging
import time
from pathlib import Path

from config.paths import USER_RECORDS_DIR
from common.types import MODE, ComparisonResults, UserStatus
from common.exceptions import UserRecordsNotExists, FiledecodeError
from common.decorators import timing_decorator

userLog = logging.getLogger(__name__)


class UserRecords:
    def __init__(self, username: str, mode: MODE = MODE.following) -> None:
        self.username = username
        self.mode = mode
        self.path = USER_RECORDS_DIR / username / mode
        self._records: list[Path] = []

    def __len__(self):
        return len(self._records)

    def __getitem__(self, index: int) -> UserSnapshot:
        """Automatically loads the file into a UserSnapshot."""
        if not self._records:
            self.refresh()

        try:
            target_path = self._records[index]
        except IndexError:
            raise UserRecordsNotExists(f"No snapshot found at index {index}")

        return self.load_snapshot(target_path)

    def refresh(self) -> None:
        """Updates the internal list of available files on disk."""
        if not self.path.exists():
            raise UserRecordsNotExists(f"No records found for {self.username}")

        files = [f for f in self.path.glob("*.json")]
        self._records = sorted(files)

    def load_snapshot(self, file_path: Path) -> UserSnapshot:
        """Reads a specific file and returns a populated UserSnapshot."""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                users = set(data["users"])

            return UserSnapshot(
                username=self.username,
                mode=self.mode,
                users=users,
                timestamp=file_path.stem
            )
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            userLog.error(f"Failed to load snapshot at {file_path}: {e}")
            raise FiledecodeError(f"Could not parse record: {file_path}")


class UserSnapshot:
    def __init__(self, username: str, mode: MODE, users: set[str], timestamp: str | None = None):
        self.username = username
        self.mode = mode
        self.users = users
        self.timestamp = timestamp or time.strftime("%Y.%m.%d %H.%M.%S")

    @timing_decorator("saving users records")
    def save(self) -> None:
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
