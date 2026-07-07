"""
GET command implementation.
"""

from cache.storage import CacheStorage
from protocol.command import Command


class GetCommand:
    """
    Executes the GET command.
    """

    @staticmethod
    def execute(
        storage: CacheStorage,
        command: Command
    ):

        if command.key is None:
            raise ValueError("Missing key")

        node = storage.get_node(command.key)

        if node is None:
            return "NULL"

        # Don't allow GET on binary data
        if node.data_type != "TEXT":
            return "ERROR: Key contains binary data. Use GET_FILE."

        return node.value.decode("utf-8")