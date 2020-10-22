from typing import Tuple

from main.model.batch.batch import Batch
from main.model.events.baseEvents import BaseEvents
from main.model.events.realizedEvents import RealizedEvents


class Events(BaseEvents):

    def __init__(self, batches: Tuple[Batch]):
        super().__init__(batches)

    @classmethod
    def create(cls, batches):
        return super().from_ids(cls, Batch, batches)

    def sample(self) -> RealizedEvents:
        return RealizedEvents(tuple([batch.sample() for batch in self.batches]))

    def __repr__(self):
        return "[ {} ]".format(", ".join(str(batch) for batch in self.batches))





