from cache.storage import CacheStorage
from protocol.command import Command


class DeleteCommand:

    @staticmethod
    def execute(storage: CacheStorage, command: Command) -> str:

        if command.key is None:
            raise ValueError("Missing key")

        deleted = storage.delete(command.key)

        if deleted:
            return "OK"

        return "NOT FOUND"