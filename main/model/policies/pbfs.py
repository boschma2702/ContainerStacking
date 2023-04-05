import math
from decimal import Decimal
from queue import PriorityQueue
from typing import Tuple, Set

from main.model.adp.valuefunctions.features.blockingContainers import blocking_containers
from main.model.batch import unique_permutations
from main.model.batch.realizedBatch import RealizedBatch
from main.model.dataclass.outcomes import terminal_unique_outcomes, handle_outbound_container, store_locations
from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events
from main.model.noSolutionError import NoSolutionError
from main.model.policies.policy import Policy
from main.model.util.prioritizedItem import PrioritizedItem


class PBFS(Policy):
    def __init__(self, events: Events, initial_terminal: Terminal):
        super().__init__(events, initial_terminal)
        self.cache_chance = {}
        # fill the cache
        self.solve(self.events, self.initial_terminal, PBFS.lower_bound_reshuffles_blocking)
        print("PBFS: Done calculating")

    def handle_realized_inbound_batch(self, terminal: Terminal, realized_batch: RealizedBatch, batch_number: int) \
            -> Tuple[Terminal, int]:
        return self.__get_best_expected_terminal(terminal_unique_outcomes(terminal, realized_batch, -1), batch_number)

    def handle_realized_outbound_batch(self, terminal: Terminal, realized_batch: RealizedBatch, batch_number: int) \
            -> Tuple[Terminal, int]:
        return self.__get_best_expected_terminal(terminal_unique_outcomes(terminal, realized_batch, -1), batch_number)

    def __get_best_expected_terminal(self, outcomes: Set[Tuple[Terminal, int]], batch_number: int) \
            -> Tuple[Terminal, int]:
        min_term = None
        # min_reshuffles = math.inf
        min_value = math.inf
        min_nr_reshuffles = math.inf
        for new_terminal, nr_reshuffles in outcomes:
            key = (batch_number+1, new_terminal.abstract())
            if key in self.cache_chance:
                expected_reshuffles = self.cache_chance[key]
                value = nr_reshuffles + expected_reshuffles
                if value < min_value:
                    min_term = new_terminal
                    min_value = value
                    min_nr_reshuffles = nr_reshuffles
        # handling an inbound move does not yield any new reshuffles
        return min_term, min_nr_reshuffles

    def solve(self, events: Events, initial_terminal: Terminal, lower_bound_function) -> Decimal:
        return self.pbfs_chance(events, 0, initial_terminal, lower_bound_function)

    def pbfs_chance(self, events: Events, t: int, initial_terminal: Terminal, lower_bound_function) -> Decimal:
        if t == events.length():
            # all events explored, thus done
            value = Decimal(0)
            abstracted = initial_terminal.abstract()
            if not (t, abstracted) in self.cache_chance:
                self.cache_chance[(t, abstracted)] = value

            return value

        current_batch = events.batch(t)

        abstract_terminal = initial_terminal.abstract()
        if (t, abstract_terminal) in self.cache_chance and not self.cache_chance[(t, abstract_terminal)].is_infinite():
            expected_value = self.cache_chance[(t, abstract_terminal)]
        else:
            value = Decimal(0)
            permutations = unique_permutations(current_batch.inbound, current_batch.containers)
            for realized_batch in permutations:
                if current_batch.inbound:
                    terminal = initial_terminal
                else:
                    terminal = initial_terminal.reveal_order(realized_batch.containers)
                intermediary_value = self.pbfs_decision(events, current_batch.inbound, t, 0, realized_batch, terminal, lower_bound_function)

                value += intermediary_value

            expected_value = value / len(permutations)
            self.cache_chance[(t, initial_terminal.abstract())] = expected_value

        return expected_value

    def pbfs_decision(self, events: Events, inbound: bool, t: int, k: int, realized_batch: RealizedBatch,
                      init_terminal: Terminal, lower_bound_function) -> Decimal:
        if k == realized_batch.length():
            # check if we completed the batch
            return self.pbfs_chance(events, t+1, init_terminal, lower_bound_function)
        elif t == events.length() - 1:
            # check if this is the last batch, can be solved using A* as problem is fully known
            # return # calculate number of reshuffles using A* if batch is outbound, else return reshuffles
            try:
                term, value = self.handle_last_batch(realized_batch, init_terminal)
                # the expected reshuffles after handling the last batch is equal to zero (as no containers are left to
                # handle anymore.
                if not (t+1, term.abstract()) in self.cache_chance:
                    self.cache_chance[(t+1, term.abstract())] = value
                return value
            except NoSolutionError:
                return Decimal('Infinity')
        else:
            if inbound:
                outcomes = store_locations(init_terminal, realized_batch.containers[k - 1], None, -1)
                if len(outcomes) == 0:
                    # print("no store locations available")
                    return Decimal('Infinity')
                is_reshuffle = False
            else:
                outcomes, is_reshuffle = handle_outbound_container(init_terminal, realized_batch.containers[k - 1], -1)

            # determine lowerbounds of the possible terminal outcomes of the handle or reshuffle
            sorted_lower_bounds = PriorityQueue()
            for term in outcomes:
                sorted_lower_bounds.put(PrioritizedItem(lower_bound_function(term, events, t), term))

            # update k if a container in the batch is handled. Do not update when a reshuffle has taken place
            new_k = k + int(not is_reshuffle)

            n_1 = sorted_lower_bounds.get(block=False).item
            min_value = self.pbfs_decision(events, inbound, t, new_k, realized_batch, n_1, lower_bound_function)
            while not sorted_lower_bounds.empty():
                item = sorted_lower_bounds.get(block=False)
                lower_bound = item.priority
                term = item.item
                if lower_bound >= min_value:
                    # lowerbound of item is worse (or equal (can only get worse)) than the actual currently min value
                    # found. No need to explore
                    break
                value = self.pbfs_decision(events, inbound, t, new_k, realized_batch, term, lower_bound_function)
                min_value = min(min_value, value)

            return int(is_reshuffle) + min_value

    @staticmethod
    def handle_last_batch(realized_batch: RealizedBatch, initial_terminal: Terminal) -> Tuple[Terminal, Decimal]:
        if realized_batch.inbound:
            raise RuntimeError("last batch should nto be an inbound batch")
        else:
            q = PriorityQueue()
            q.put(PrioritizedItem((Decimal(0), 0), initial_terminal))

            while not q.empty():
                item = q.get()
                term: Terminal = item.item
                (reshuffles, i) = item.priority
                i = abs(i)

                # check if done
                if i == realized_batch.length():
                    return term, reshuffles

                current_container = realized_batch.containers[i]
                current_block, current_stack, current_tier = term.container_location(current_container)
                blocking_containers = term.blocking_containers((current_block, current_stack, current_tier))

                if len(blocking_containers) > 0:
                    # try all reshuffle locations
                    term, container = term.retrieve_container((current_block, current_stack))
                    for reshuffle_term in store_locations(term, container, (current_block, current_stack, current_tier), -1):
                        q.put(PrioritizedItem((reshuffles+1, -i), reshuffle_term))
                else:
                    # retrieve current container in batch
                    new_term = term.retrieve_container((current_block, current_stack))[0]
                    q.put(PrioritizedItem((reshuffles, -(i+1)), new_term))

            raise NoSolutionError("No solution found")

    @staticmethod
    def lower_bound_reshuffles_blocking(terminal: Terminal, event: Events, t: int):
        # if batch_label*2 + 1 > nr_batches then container is not being handled in the given planning horizon
        # differently phrased: if batch_label <= nr_batches // 2 it will be handled.
        return blocking_containers(terminal, event, t, None)
