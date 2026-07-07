"""
SET command implementation.
"""

from cache.storage import CacheStorage
from protocol.command import Command


class SetCommand:
    """
    Executes the SET command.
    """

    @staticmethod
    def execute(storage: CacheStorage, command: Command) -> str:
        """
        Stores a key-value pair in the cache.
        """

        storage.set(
            command.key,
            command.value,
            data_type="TEXT",
            ttl=command.ttl
        )

        return "OK"