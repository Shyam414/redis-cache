from cache.storage import CacheStorage
from protocol.command import Command


class SetCommand:

    @staticmethod
    def execute(
        storage: CacheStorage,
        command: Command,
    ) -> str:

        if command.key is None:
            raise ValueError("Missing key")

        if command.value is None:
            raise ValueError("Missing value")

        storage.set(
            command.key,
            command.value,
            data_type="TEXT",
            ttl=command.ttl,
        )

        return "OK"