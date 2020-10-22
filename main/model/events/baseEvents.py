import math
import operator
from functools import reduce
from typing import Tuple, List

from main.model.batch.baseBatch import BaseBatch


class BaseEvents:

    def __init__(self, batches: Tuple[BaseBatch]):
        self.batches = batches

    def batch(self, i):
        return self.batches[i]

    def length(self):
        return len(self.batches)

    def max_number_realisations(self):
        return reduce(operator.mul, [math.factorial(batch.length()) for batch in self.batches], 1)

    @staticmethod
    def from_ids(event_class, batch_class, batches: List[Tuple[int, ...]]):
        """
        Helper function to create batches easily.
        Example:
            [(1,2), (1,), (3,4,5), (2,3,4)]
            container 1,2 arrives in first batch and departs. Then 3,4,5 arrive and 2,3,4 depart.
            Batch labels:
                1 -> 0
                2 -> 1
                3 -> 1
                4 -> 1
                5 -> 2
        :return: A instance of BaseEvents (either Events or RealizedEvents depending from where it is called)
        """
        batch_labels = {}
        container_dict = {}
        for i in range(1, len(batches), 2):
            outbound_batch = batches[i]
            for container_id in outbound_batch:
                batch_labels[container_id] = i//2

        default_label = (len(batches) // 2)
        batch_list = []
        for i in range(len(batches)):
            batch = batches[i]
            current_batch = []
            inbound = i % 2 == 0
            if inbound:
                for container_id in batch:
                    container = (container_id, batch_labels.get(container_id, default_label), -1)
                    if container_id in container_dict:
                        raise ValueError("ID of container already used: ID {}".format(container_id))
                    container_dict[container_id] = container
                    current_batch.append(container)
            else:
                for container_id in batch:
                    current_batch.append(container_dict.get(container_id))

            batch_list.append(batch_class(inbound, tuple(current_batch)))
        return event_class(batch_list)

    def __repr__(self):
        return "[ {} ]".format(", ".join(str(batch) for batch in self.batches))
