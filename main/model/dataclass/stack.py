from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from main.model.dataclass import Container


@dataclass
class Stack:
    __slots__ = ['containers', 'abstract_containers', 'blocking_lowerbound']
    containers: Tuple[Container, ...]
    abstract_containers: Tuple[Container, ...]
    blocking_lowerbound: float

    def __init__(self, containers: Tuple[Container, ...]):
        self.containers = containers
        self.abstract_containers = self.calc_abstract_containers()
        self.blocking_lowerbound = self.calc_blocking_lowerbound()

    def calc_blocking_lowerbound(self) -> float:
        """
        Formula for calculating the number of blocking containers whithin a stack. Formula from (Galle et.al., 2018)
        :return: number of blocking containers
        """
        c = [container[1] for container in self.containers]
        height = len(self.containers)
        return height - sum([int(c[h] == min(c[0:h + 1]))/sum([int(c[h] == ci) for ci in c[0:h + 1]]) for h in range(height)])

    def calc_abstract_containers(self):
        return tuple([(0, c[1], c[2]) for c in self.containers])

    @classmethod
    def empty(cls) -> Stack:
        return cls(())

    # @lru_cache(1)
    def abstract(self) -> Stack:
        return Stack(self.abstract_containers)

    def store_container(self, container: Container) -> Stack:
        return Stack(self.containers + (container,))

    # @lru_cache(1)
    def retrieve_container(self) -> Tuple[Stack, Container]:
        return Stack(self.containers[:-1]), self.containers[-1]

    def reveal_order(self, order_dict: dict) -> Stack:
        return Stack(tuple([Stack.__reveal_container(container, order_dict) for container in self.containers]))

    def height(self):
        return len(self.containers)

    def __repr__(self):
        return "-" + "∣".join([Stack.__container_to_string(container) for container in self.containers]) + "\n"

    def __eq__(self, other):
        return self.abstract_containers == other.abstract_containers
        # return Stack.__container_abstract(self) == Stack.__container_abstract(other)

    def __lt__(self, other):
        return self.abstract_containers < other.abstract_containers

    # @lru_cache(1)
    def __hash__(self):
        return hash(self.abstract_containers)

    @staticmethod
    def __reveal_container(container: Container, order_dict: dict) -> Container:
        return container[0], container[1], order_dict.get(container[0], -1)

    @staticmethod
    def __container_to_string(container: Container):
        identifier = str(container[0])
        batch_label = str(container[1])
        if container[2] == -1:
            order_label = "?"
        else:
            order_label = str(container[2])
        return "{}_{}({})".format(batch_label, order_label, identifier)

    def containers_above(self, tier) -> Tuple[Container, ...]:
        return self.containers[tier + 1:]

    def blocking_containers(self, included_batch_labels) -> int:
        total = 0
        for i in reversed(range(self.height())):
            total += self.blocking(i, included_batch_labels)
        return total

    def blocking(self, tier, included_batch_labels) -> int:
        for i_below in reversed(range(tier)):
            if self.containers[i_below][1] <= included_batch_labels and self.containers[i_below] < self.containers[tier]:
                return 1
        return 0

    def min_container(self):
        # returns first departing container
        return min(self.containers, key=lambda x: x[1:])
