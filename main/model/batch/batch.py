import random
from itertools import permutations
from typing import Tuple

from main.model.batch import unique_permutations
from main.model.batch.baseBatch import BaseBatch
from main.model.batch.realizedBatch import RealizedBatch
from main.model.dataclass import Container


class Batch(BaseBatch):

    def __init__(self, inbound: bool, containers: Tuple[Container, ...]):
        super().__init__(inbound, containers)

    def unique_permutations(self):
        # can be done to speed up inbound batches, but messes up chance calculation
        # return [x for x in set(permutations(self.containers))]
        # return [x for x in permutations(self.containers)]
        return unique_permutations(self.inbound, self.containers)

    def is_empty(self):
        return len(self.containers) == 0

    def sample(self) -> RealizedBatch:
        return RealizedBatch(self.inbound, tuple(random.sample(self.containers, self.length())))

    def __repr__(self):
        return "{{ {} }}{}".format(", ".join([str(c) for c in self.containers]), self.bound_label())
