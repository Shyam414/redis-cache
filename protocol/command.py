from dataclasses import dataclass
from typing import Optional


@dataclass
class Command:
    # Command type
    command: str

    # Cache key
    key: Optional[str] = None

    # Used for SET
    value: Optional[bytes] = None

    # Used for SET_FILE
    file_size: Optional[int] = None

    # Optional metadata
    file_name: Optional[str] = None

    ttl: Optional[int] = None