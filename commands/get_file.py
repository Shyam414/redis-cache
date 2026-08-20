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

        node = storage.get_node(command.key)

        if node is None:
            return None

        if node.data_type != "FILE":
            raise ValueError(
                "Key does not contain a file."
            )

        return node.value