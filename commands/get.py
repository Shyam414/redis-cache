from cache.storage import CacheStorage
from protocol.command import Command


class GetCommand:

    @staticmethod
    def execute(
        storage: CacheStorage,
        command: Command,
    ):

        if command.key is None:
            raise ValueError("Missing key")

        value = storage.get_text(
            command.key
        )

        if value is None:
            return "NULL"

        return value