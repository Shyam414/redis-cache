from typing import Optional
import threading
import time

from cache.node import CacheNode
from cache.lru import LRUCache


class CacheStorage:

    def __init__(
        self,
        max_memory: int = 100 * 1024 * 1024,
    ):
        self.max_memory = max_memory
        self.current_memory = 0
        self.cache: dict[str, CacheNode] = {}
        self.lru = LRUCache()
        self.lock = threading.RLock()

    def set(
        self,
        key: str,
        value: bytes,
        data_type: str = "TEXT",
        ttl: Optional[int] = None,
    ) -> None:

        value_size = len(value)

        if value_size > self.max_memory:
            raise ValueError(
                f"Object too large ({value_size} bytes). "
                f"Cache limit = {self.max_memory} bytes."
            )

        expiry_time = (
            time.time() + ttl
            if ttl is not None
            else None
        )

        with self.lock:

            node = self.cache.get(key)

            if node is not None:

                self.lru.remove(node)

                self.current_memory -= node.size

                while (
                    self.current_memory + value_size
                    > self.max_memory
                ):
                    removed = self.lru.remove_least_recent()

                    if removed is None:
                        break

                    self.current_memory -= removed.size
                    self.cache.pop(removed.key, None)

                node.value = value
                node.size = value_size
                node.data_type = data_type
                node.expiry_time = expiry_time

                self.current_memory += value_size
                self.lru.add_to_front(node)

                return

            while (
                self.current_memory + value_size
                > self.max_memory
            ):
                removed = self.lru.remove_least_recent()

                if removed is None:
                    break

                self.current_memory -= removed.size
                self.cache.pop(removed.key, None)

            node = CacheNode(
                key=key,
                value=value,
                data_type=data_type,
                size=value_size,
                expiry_time=expiry_time,
            )

            self.cache[key] = node
            self.current_memory += value_size
            self.lru.add_to_front(node)

    def get_text(self,key: str,) -> str | None:

        with self.lock:
            node = self.cache.get(key)
            if node is None:
                return None

            if node.is_expired():
                self._delete_node(node)
                return None

            if node.data_type != "TEXT":
                raise ValueError(
                    "Key contains binary data. "
                    "Use GET_FILE."
                )
            self.lru.move_to_front(node)

            return node.value.decode("utf-8")

    def get_file(self,key: str,) -> bytes | None:

        with self.lock:
            node = self.cache.get(key)
            if node is None:
                return None

            if node.is_expired():
                self._delete_node(node)
                return None

            if node.data_type != "FILE":
                raise ValueError(
                    "Key does not contain a file."
                )
            self.lru.move_to_front(node)

            return node.value
    
    def delete(self, key: str) -> bool:

        with self.lock:

            node = self.cache.get(key)

            if node is None:
                return False

            self._delete_node(node)

            return True

    def exists(self, key: str) -> bool:

        with self.lock:

            node = self.cache.get(key)

            if node is None:
                return False

            if node.is_expired():
                self._delete_node(node)
                return False

            return True

    def size(self) -> int:

        with self.lock:
            self._remove_expired()
            return len(self.cache)

    def memory_usage(self) -> int:

        with self.lock:
            return self.current_memory

    def clear(self) -> None:

        with self.lock:
            self.cache.clear()
            self.current_memory = 0
            self.lru = LRUCache()

    def keys(self) -> list[str]:

        with self.lock:
            self._remove_expired()
            return list(self.cache.keys())

    def expire(
        self,
        key: str,
        ttl: int,
    ) -> bool:

        with self.lock:

            node = self.cache.get(key)

            if node is None:
                return False

            if node.is_expired():
                self._delete_node(node)
                return False

            node.expiry_time = time.time() + ttl

            return True

    def remove_expired(self) -> int:

        with self.lock:
            return self._remove_expired()

    def _delete_node(
        self,
        node: CacheNode,
    ) -> None:

        existing = self.cache.get(node.key)

        if existing is not node:
            return

        self.lru.remove(node)
        self.current_memory -= node.size
        del self.cache[node.key]

    def _remove_expired(self) -> int:

        expired_keys = [
            key
            for key, node in self.cache.items()
            if node.is_expired()
        ]

        for key in expired_keys:
            node = self.cache.get(key)

            if node is not None and node.is_expired():
                self._delete_node(node)

        return len(expired_keys)