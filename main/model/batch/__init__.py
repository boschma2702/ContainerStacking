from itertools import permutations
from typing import Tuple

from main.model.batch.realizedBatch import RealizedBatch
from main.model.dataclass import Container


def unique_permutations(inbound: bool, containers: Tuple[Container, ...]):
    # can be done to speed up inbound batches, but messes up chance calculation
    # return [x for x in set(permutations(self.containers))]
    # return [x for x in permutations(self.containers)]
    return [RealizedBatch(inbound, x) for x in permutations(containers)]
