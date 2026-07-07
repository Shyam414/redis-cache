"""
SET_FILE command implementation.
"""

from cache.storage import CacheStorage
from protocol.command import Command


class SetFileCommand:
    """
    Stores binary data (image, video, pdf, etc.)
    inside the cache.
    """

    @staticmethod
    def execute(
        storage: CacheStorage,
        command: Command
    ) -> str:

        if command.key is None:
            raise ValueError("Missing key")

        if command.value is None:
            raise ValueError("No file data received")

        storage.set(
            command.key,
            command.value,
            data_type="FILE"
        )

        return "FILE STORED"