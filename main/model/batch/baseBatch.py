from typing import Tuple

from main.model.dataclass import Container


class BaseBatch:

    def __init__(self, inbound: bool, containers: Tuple[Container, ...]):
        self.inbound = inbound
        self.containers = containers

    def length(self):
        return len(self.containers)

    def is_empty(self):
        return self.length() == 0

    def bound_label(self):
        if self.inbound:
            return "in"
        else:
            return "out"