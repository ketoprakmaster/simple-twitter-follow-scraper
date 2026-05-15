from enum import StrEnum
from dataclasses import dataclass, field


class MODE(StrEnum):
    following = "following"
    followers = "followers"

class UserStatus(StrEnum):
    EXISTS      = "Exists"
    BANNED      = "Banned"
    DEACTIVATED = "Deactivated"
    WITHHELD    = "Withheld"
    MISSING     = "Missing"

@dataclass
class ComparisonResults:
    removed: dict[str, UserStatus] = field(default_factory=dict)
    added: set[str] = field(default_factory=set)

    def get_false_negatives(self) -> set[str]:
        """Returns users who were thought to be removed but actually still exist."""
        return {user for user, status in self.removed.items() if status == UserStatus.EXISTS}

    @property
    def has_actual_changes(self) -> bool:
        """Checks if there are added users or users who are truly gone (Banned/Missing)."""
        real_removals = any(status != UserStatus.EXISTS for status in self.removed.values())
        return bool(self.added or real_removals)

    async def check_status(self, driver: 'twitterDriver'):
        """
        Enriches the 'removed' dict by checking live status via the driver.
        """
        for handle in list(self.removed.keys()):
            status = await driver.check_user_status(handle)
            self.removed[handle] = status
