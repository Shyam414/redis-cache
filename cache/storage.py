from typing import Optional
import time

from cache.node import CacheNode
from cache.lru import LRUCache


class CacheStorage:

    def __init__(
        self,
        max_memory: int = 100 * 1024 * 1024,
    ):

        # Maximum cache size (bytes)
        self.max_memory = max_memory

        # Currently used memory
        self.current_memory = 0

        # key -> CacheNode
        self.cache: dict[str, CacheNode] = {}

        # LRU manager
        self.lru = LRUCache()

    def set(
        self,
        key: str,
        value: bytes,
        data_type: str = "TEXT",
        ttl: Optional[int] = None
    ) -> None:

        value_size = len(value)

        if value_size > self.max_memory:
            raise ValueError(
                f"Object too large ({value_size} bytes). "
                f"Cache limit = {self.max_memory} bytes."
            )

        expiry_time = None

        if ttl is not None:
            expiry_time = time.time() + ttl

        # -------------------------
        # Update Existing Key
        # -------------------------

        if key in self.cache:

            node = self.cache[key]

            # Calculate memory after update
            new_memory = (
                self.current_memory
                - node.size
                + value_size
            )

            # Evict other keys if required
            while new_memory > self.max_memory:

                removed = self.lru.remove_least_recent()

                if removed is None:
                    break

                # Don't evict the same node
                if removed.key == key:
                    self.lru.add_to_front(removed)
                    break

                print(f"Evicted: {removed.key}")

                self.current_memory -= removed.size

                del self.cache[removed.key]

                new_memory = (
                    self.current_memory
                    - node.size
                    + value_size
                )

            self.current_memory -= node.size

            node.value = value
            node.size = value_size
            node.data_type = data_type
            node.expiry_time = expiry_time

            self.current_memory += value_size

            self.lru.move_to_front(node)

            return

        # -------------------------
        # New Key
        # -------------------------

        while (
            self.current_memory + value_size
            > self.max_memory
        ):

            removed = self.lru.remove_least_recent()

            if removed is None:
                break

            print(f"Evicted: {removed.key}")

            self.current_memory -= removed.size

            del self.cache[removed.key]

        node = CacheNode(
            key=key,
            value=value,
            data_type=data_type,
            size=value_size,
            expiry_time=expiry_time
        )

        self.cache[key] = node

        self.current_memory += value_size

        self.lru.add_to_front(node)

    def get(self, key: str) -> Optional[bytes]:

        node = self.cache.get(key)

        if node is None:
            return None

        if node.is_expired():

            self.delete(key)

            return None

        self.lru.move_to_front(node)

        return node.value

    def get_node(self, key: str) -> Optional[CacheNode]:

        node = self.cache.get(key)

        if node is None:
            return None

        if node.is_expired():

            self.delete(key)

            return None

        self.lru.move_to_front(node)

        return node

    def delete(self, key: str) -> bool:

        node = self.cache.get(key)

        if node is None:
            return False

        self.lru.remove(node)

        self.current_memory -= node.size

        del self.cache[key]

        return True

    def exists(self, key: str) -> bool:

        return self.get_node(key) is not None

    def size(self) -> int:

        return len(self.keys())

    def memory_usage(self) -> int:

        return self.current_memory

    def clear(self) -> None:

        self.cache.clear()

        self.current_memory = 0

        self.lru = LRUCache()

    def keys(self) -> list[str]:

        valid_keys = []

        for key in list(self.cache.keys()):

            node = self.cache[key]

            if node.is_expired():

                self.delete(key)

                continue

            valid_keys.append(key)

        return valid_keys
