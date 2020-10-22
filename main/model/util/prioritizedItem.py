from functools import total_ordering


@total_ordering
class PrioritizedItem:
    def __init__(self, priority, item):
        self.priority = priority
        self.item = item

    def __eq__(self, other):
        if not isinstance(other, __class__):
            return NotImplemented
        return self.priority == other.priority

    def __lt__(self, other):
        if not isinstance(other, __class__):
            return NotImplemented
        return self.priority < other.priority
