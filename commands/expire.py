"""
EXPIRE command implementation.
"""

import time

from cache.storage import CacheStorage
from protocol.command import Command


class ExpireCommand:


    @staticmethod
    def execute(
        storage: CacheStorage,
        command: Command
    ):

        if command.key is None:

            raise ValueError(
                "Missing key"
            )


        if command.ttl is None:

            raise ValueError(
                "Missing TTL"
            )


        node = storage.get_node(
            command.key
        )


        if node is None:

            return 0


        node.expiry_time = (
            time.time()
            +
            command.ttl
        )


        return 1