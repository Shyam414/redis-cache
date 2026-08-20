from cache.node import CacheNode


class LRUCache:

    def __init__(self):
        self.head = CacheNode(key="HEAD", value=b"")
        self.tail = CacheNode(key="TAIL", value=b"")

        self.head.next = self.tail
        self.tail.prev = self.head

    def remove(self, node: CacheNode):

        if node is self.head or node is self.tail:
            return

        prev_node = node.prev
        next_node = node.next

        if prev_node is None or next_node is None:
            return

        prev_node.next = next_node
        next_node.prev = prev_node

        node.prev = None
        node.next = None

    def add_to_front(self, node: CacheNode):

        if node is self.head or node is self.tail:
            return

        first = self.head.next

        node.prev = self.head
        node.next = first

        self.head.next = node
        first.prev = node

    def move_to_front(self, node: CacheNode):

        self.remove(node)
        self.add_to_front(node)

    def remove_least_recent(self):

        if self.tail.prev is self.head:
            return None

        lru_node = self.tail.prev

        self.remove(lru_node)

        return lru_node