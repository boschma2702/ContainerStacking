import math
from queue import PriorityQueue
from typing import Tuple, Set

from main.model.batch import RealizedBatch
from main.model.dataclass.outcomes import terminal_unique_outcomes, store_locations, handle_outbound_container
from main.model.dataclass.terminal import Terminal
from main.model.noSolutionError import NoSolutionError
from main.model.policies.policy import Policy
from main.model.util.prioritizedItem import PrioritizedItem


class Myopic(Policy):

    def handle_realized_inbound_batch(self, terminal: Terminal, realized_batch: RealizedBatch, batch_number: int, container_labels: dict) \
            -> Tuple[Terminal, int]:
        return lowest_inbound_outcome(terminal, realized_batch, container_labels)

    def handle_realized_outbound_batch(self, terminal: Terminal, realized_batch: RealizedBatch, batch_number: int, container_labels: dict) \
            -> Tuple[Terminal, int]:
        return lowest_outbound_outcome(terminal, realized_batch, container_labels)


def lowest_inbound_outcome(initial_terminal: Terminal, batch: RealizedBatch, container_labels: dict) -> Tuple[Terminal, int]:
    # q = ((reshuffles, -i)), term)
    q = PriorityQueue()
    q.put(PrioritizedItem((0, 0), initial_terminal))
    abstract_added = set()

    while not q.empty():
        item = q.get(block=False)
        (reshuffles, i) = item.priority
        i = -i
        terminal = item.item

        # check if this is end state
        if i == batch.length():
            return terminal, reshuffles
        else:
            # not yet finished
            current_container = batch.containers[i]
            store_outcomes = store_locations(terminal, current_container, None, -1, container_labels)
            for new_term in store_outcomes:
                new_term_abstracted = new_term.abstract()
                if new_term_abstracted not in abstract_added:
                    new_i = i + 1
                    abstract_added.add(new_term_abstracted)
                    q.put(PrioritizedItem((reshuffles, -new_i), new_term))

    raise NoSolutionError("Could not find suitable solutions for batch: {}\n terminal:\n{}".format(batch, initial_terminal))


def lowest_outbound_outcome(initial_terminal: Terminal, batch: RealizedBatch, container_labels) -> Tuple[Terminal, int]:
    # q = ((reshuffles, -i)), term)
    q = PriorityQueue()
    q.put(PrioritizedItem((0, 0), initial_terminal))
    abstract_added = set()

    while not q.empty():
        item = q.get(block=False)
        (reshuffles, i) = item.priority
        i = -i
        terminal = item.item

        # check if this is end state
        if i == batch.length():
            return terminal, reshuffles
        else:
            # not yet explored, need to add children to queue
            current_container = batch.containers[i]
            # store_outcomes = __store_locations(terminal, current_container, None)
            handling_outcomes, is_reshuffle = handle_outbound_container(terminal, current_container, -1, container_labels)
            new_i = i + int(not is_reshuffle)
            new_reshuffles = reshuffles + int(is_reshuffle)
            for new_term in handling_outcomes:
                new_term_abstracted = new_term.abstract()
                if new_term_abstracted not in abstract_added:
                    abstract_added.add(new_term_abstracted)
                    q.put(PrioritizedItem((new_reshuffles, -new_i), new_term))

    raise NoSolutionError("Could not find suitable solutions for batch: {}\n terminal:\n{}".format(batch, initial_terminal))

