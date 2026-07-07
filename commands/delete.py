"""
DEL command implementation.
"""

from cache.storage import CacheStorage
from protocol.command import Command


class DeleteCommand:
    """
    Executes the DEL command.
    """

    @staticmethod
    def execute(storage: CacheStorage, command: Command) -> str:
        """
        Deletes a key from the cache.
        """

        deleted = storage.delete(command.key)

        if deleted:
            return "OK"

        return "NOT FOUND"