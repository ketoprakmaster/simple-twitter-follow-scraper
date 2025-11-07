from enum import StrEnum
from dataclasses import dataclass, field

class MODE(StrEnum):
    following = "following"
    followers = "followers" 

# struct for records comparison
@dataclass(frozen=True)
class ComparisonResults():
    removed: set[str] = field(default_factory=set)
    added: set[str] = field(default_factory=set)


