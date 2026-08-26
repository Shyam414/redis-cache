from cache.storage import CacheStorage
from protocol.command import Command


class GetFileCommand:

    @staticmethod
    def execute(
        storage: CacheStorage,
        command: Command,
    ):

        if command.key is None:
            raise ValueError("Missing key")

        file_data = storage.get_file(
            command.key
        )

        if file_data is None:
            return None

        return file_data