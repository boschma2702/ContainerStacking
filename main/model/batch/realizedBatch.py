from typing import Tuple, Container

from main.model.batch.baseBatch import BaseBatch


class RealizedBatch(BaseBatch):

    def __init__(self, inbound: bool, containers: Tuple[Container, ...]):
        super().__init__(inbound, containers)

    def __repr__(self):
        return "[ {} ]{}".format(", ".join([str(c) for c in self.containers]), self.bound_label())