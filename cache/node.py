from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class CacheNode:

    key: str

    # Supports text, images, videos, etc.
    value: bytes

    # Memory used by this value
    size: int = 0

    data_type: str="TEXT"
    # Used later for TTL
    expiry_time: Optional[float] = None

    # Used later for LFU
    frequency: int = 0

    # Used for LRU
    prev: Optional["CacheNode"] = None
    next: Optional["CacheNode"] = None


    def is_expired(self) -> bool:

        if self.expiry_time is None:
            return False

        return time.time() > self.expiry_time