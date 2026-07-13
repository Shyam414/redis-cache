from cache.storage import CacheStorage
from protocol.command import Command


class SetCommand:

    @staticmethod
    def execute(storage: CacheStorage, command: Command) -> str:

        storage.set(
            command.key,
            command.value,
            data_type="TEXT",
            ttl=command.ttl
        )

        return "OK"