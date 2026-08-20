from cache.storage import CacheStorage
from protocol.command import Command


class ExpireCommand:

    @staticmethod
    def execute(
        storage: CacheStorage,
        command: Command,
    ):

        if command.key is None:
            raise ValueError("Missing key")

        if command.ttl is None:
            raise ValueError("Missing TTL")

        if command.ttl < 0:
            raise ValueError("TTL cannot be negative")

        updated = storage.expire(
            command.key,
            command.ttl,
        )

        return 1 if updated else 0