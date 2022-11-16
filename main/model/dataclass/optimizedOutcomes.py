import math
import random
from typing import Tuple, Optional, List

from main.model.adp.valuefunctions.valueFunctionApproximation import ValueFunctionApproximate
from main.model.batch.realizedBatch import RealizedBatch
from main.model.dataclass import Container, StackLocation, StackTierLocation
from main.model.dataclass.outcomes import valid_store_location, corridor
from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events
from main.model.noSolutionError import NoSolutionError


def terminal_optimized_outcome(terminal: Terminal,
                               batch: RealizedBatch,
                               value_function_approx: ValueFunctionApproximate,
                               n: int,
                               t: int,
                               event: Events,
                               corridor_size: int,
                               corridor_size_feature: int,
                               random_choice: bool) \
        -> Tuple[Terminal, int, float]:
    if batch.length() == 0:
        return terminal, 0, value_function_approx.value_approximate(n, t, terminal, event)
    if batch.inbound:
        return _optimized_inbound_outcome(terminal, batch, value_function_approx, n, t, event, random_choice,
                                          corridor_size, corridor_size_feature)
    else:
        return _optimized_outbound_outcome(terminal.reveal_order(batch.containers), batch, value_function_approx, n, t,
                                           event, random_choice, corridor_size, corridor_size_feature)


def _optimized_inbound_outcome(initial_terminal: Terminal,
                               batch: RealizedBatch,
                               value_function_approx: ValueFunctionApproximate,
                               n: int,
                               t: int,
                               event: Events,
                               random_choice: bool,
                               corridor_size: int,
                               corridor_size_feature: int) -> Tuple[Terminal, int, float]:
    current_terminal = initial_terminal
    value = None
    for target_container in batch.containers:
        # find best terminal layout according to the value function approx
        if not random_choice:
            current_terminal, value = optimized_store_location(current_terminal, value_function_approx, n, t, event,
                                                               target_container, None, corridor_size,
                                                               corridor_size_feature)
        else:
            # pick random spot
            valid_locations = valid_store_locations(current_terminal, None, corridor_size)
            stack_location = random.choice(valid_locations)
            current_terminal = current_terminal.store_container(stack_location, target_container)
            value = value_function_approx.value_approximate(n, t, current_terminal, event)

    return current_terminal, 0, value


def _optimized_outbound_outcome(initial_terminal: Terminal,
                                batch: RealizedBatch,
                                value_function_approx: ValueFunctionApproximate,
                                n: int,
                                t: int,
                                event: Events,
                                random_choice: bool,
                                corridor_size: int,
                                corridor_size_feature: int) \
        -> Tuple[Terminal, int, float]:
    current_terminal = initial_terminal
    reshuffles = 0
    for target_container in batch.containers:
        target_location = current_terminal.container_location(target_container)
        blocking_containers = current_terminal.blocking_containers(target_location)

        if len(blocking_containers) > 0:
            reshuffles += len(blocking_containers)
            for blocking_container in blocking_containers:
                blocking_container_location = current_terminal.container_location(blocking_container)
                term, retrieved_container = current_terminal.retrieve_container(blocking_container_location[:2])
                assert blocking_container[0] == retrieved_container[0]

                if not random_choice:
                    current_terminal, value = optimized_store_location(term, value_function_approx, n, t, event,
                                                                       blocking_container, target_location,
                                                                       corridor_size, corridor_size_feature)
                else:
                    # Reshuffle to random locations
                    valid_locations = valid_store_locations(current_terminal, target_location, corridor_size)
                    stack_location = random.choice(valid_locations)
                    current_terminal = term.store_container(stack_location, blocking_container)

        current_terminal, retrieved_container = current_terminal.retrieve_container(target_location[:-1])
        assert retrieved_container[0] == target_container[
            0], "retrieved container ({}) not same as target container ({}) in terminal:\n{}".format(
            retrieved_container, target_container, initial_terminal)
    return current_terminal, reshuffles, value_function_approx.value_approximate(n, t, current_terminal, event)


def optimized_store_location(terminal: Terminal,
                             value_function_approx: ValueFunctionApproximate,
                             n: int,
                             t: int,
                             event: Events,
                             container: Container,
                             exclude_target_stack_tier_location: Optional[StackTierLocation],
                             corridor_size: int,
                             corridor_size_feature: int
                             ) -> Tuple[Terminal, float]:
    min_value = math.inf
    min_terminal = None
    corridor_list = corridor(terminal, exclude_target_stack_tier_location, corridor_size)

    # determine corridor for feature
    if corridor_size == corridor_size_feature:
        corridor_list_feature = corridor_list
    else:
        corridor_list_feature = corridor(terminal, exclude_target_stack_tier_location, corridor_size_feature)

    for block_index in corridor_list:
        block = terminal.blocks[block_index]
        for stack_index in range(len(block.stacks)):
            stack_location = (block_index, stack_index)
            # check if container may be placed in this location
            if valid_store_location(terminal, stack_location, exclude_target_stack_tier_location):
                new_term = terminal.store_container((block_index, stack_index), container)
                value = value_function_approx.value_approximate(n, t, new_term, event, corridor_list_feature)
                if value < min_value:
                    min_value = value
                    min_terminal = new_term

    if min_terminal is None:
        raise NoSolutionError("Could not find suitable solutions for container: {}\n terminal:\n{}"
                              .format(container, terminal))
    return min_terminal, value_function_approx.value_approximate(n, t, min_terminal, event)


def valid_store_locations(terminal: Terminal, exclude_target_stack_tier_location: Optional[StackTierLocation],
                          corridor_size: int) -> List[StackLocation]:
    valid_locations = []
    for block_index in corridor(terminal, exclude_target_stack_tier_location, corridor_size):
        block = terminal.blocks[block_index]
        for stack_index in range(len(block.stacks)):
            stack_location = (block_index, stack_index)
            # check if container may be placed in this location
            if valid_store_location(terminal, stack_location, exclude_target_stack_tier_location):
                valid_locations.append(stack_location)

    if len(valid_locations) == 0:
        raise NoSolutionError("Could not find suitable solutions for (to exclude: {}) terminal:\n{}"
                              .format(exclude_target_stack_tier_location, terminal))

    return valid_locations
