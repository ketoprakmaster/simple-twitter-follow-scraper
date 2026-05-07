from enum import StrEnum
from dataclasses import dataclass, field
from pathlib import Path

class MODE(StrEnum):
    following = "following"
    followers = "followers"

class UserStatus(StrEnum):
    MISSING = "Missing"
    BANNED = "Banned"
    EXISTS = "Exists"

@dataclass(frozen=True)
class UserRecords:
    username: str
    mode: MODE
    users: set[str]
    file_path: Path | None = None

@dataclass
class ComparisonResults:
    removed: dict[str, UserStatus] = field(default_factory=dict)
    added: set[str] = field(default_factory=set)

    @property
    def has_changes(self) -> bool:
        return bool(self.removed or self.added)

    async def check_status(self, driver: 'twitterDriver'):
        """
        Enriches the 'removed' dict by checking live status via the driver.
        """
        for handle in list(self.removed.keys()):
            status = await driver.check_user_status(handle)
            self.removed[handle] = status
