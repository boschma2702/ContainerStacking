from typing import Tuple

from main.model.batch.realizedBatch import RealizedBatch
from main.model.events.baseEvents import BaseEvents


class RealizedEvents(BaseEvents):

    def __init__(self, realized_batches: Tuple[RealizedBatch]):
        super().__init__(realized_batches)

    @classmethod
    def create(cls, batches):
        return super().from_ids(cls, RealizedBatch, batches)