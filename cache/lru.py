from cache.node import CacheNode


class LRUCache:

    def __init__(self):

        # Dummy nodes
        self.head = CacheNode(key="HEAD",value=b"")
        self.tail = CacheNode(key="TAIL",value=b"")
        self.head.next = self.tail
        self.tail.prev = self.head


    def remove(self, node: CacheNode):

        prev_node = node.prev
        next_node = node.next

        prev_node.next = next_node
        next_node.prev = prev_node


    def add_to_front(self, node: CacheNode):

        first = self.head.next

        node.next = first
        node.prev = self.head

        self.head.next = node
        first.prev = node


    def move_to_front(self, node: CacheNode):

        self.remove(node)
        self.add_to_front(node)


    def remove_least_recent(self):

        if self.tail.prev == self.head:
            return None

        lru_node = self.tail.prev

        self.remove(lru_node)

        return lru_node