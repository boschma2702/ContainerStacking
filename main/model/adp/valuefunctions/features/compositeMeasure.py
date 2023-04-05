from typing import Optional, Set, List, Tuple

from main.model.adp.valuefunctions.features.MMRule import MM_rule
from main.model.adp.valuefunctions.features.mmAdopted import MM_adopted_rule
from main.model.adp.valuefunctions.features.util.getAllContainers import get_all_containers
from main.model.adp.valuefunctions.features.util.getBlocks import get_blocks, get_block_indices
from main.model.adp.valuefunctions.features.util.validStacks import get_valid_stacks
from main.model.dataclass import StackLocation, Container, StackTierLocation
from main.model.dataclass.block import Block
from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events

ALPHA = 0.65


def composite_adopted_measure(terminal: Terminal, event: Events, current_batch_number: int, corridor: Optional[List[int]], container_labels: dict):
    included_block_indices = get_block_indices(terminal, corridor)
    mmrule_score = MM_adopted_rule(terminal, included_block_indices, container_labels)
    crl_score = crl(terminal, included_block_indices, container_labels)
    return ALPHA * mmrule_score + (1-ALPHA) * crl_score


def composite_measure(terminal: Terminal, event: Events, current_batch_number: int, corridor: Optional[List[int]], container_labels: dict):
    included_block_indices = get_block_indices(terminal, corridor)
    mmrule_score = MM_rule(terminal, included_block_indices, container_labels)
    crl_score = crl(terminal, included_block_indices, container_labels)
    return ALPHA * mmrule_score + (1-ALPHA) * crl_score


def crl(terminal: Terminal, included_block_indices: List[int], container_labels: dict) -> float:
    # determine order of container retrieval
    retrieval_order = get_all_containers(terminal, included_block_indices)
    retrieval_order.sort(key=lambda x: x[1:])
    removed_containers = set()

    current_terminal = terminal
    total_reshuffles = 0

    for target_container in retrieval_order:
        if target_container not in removed_containers:
            target_container_location = current_terminal.container_location(target_container)

            # check if blocking containers cause new blockings
            blocking_containers: List[Container] = current_terminal.blocking_containers(target_container_location)
            total_reshuffles += len(blocking_containers)
            for blocking_container in blocking_containers:
                blocking_location = current_terminal.container_location(blocking_container)
                current_terminal, _ = current_terminal.retrieve_container(blocking_location)
                removed_containers.add(blocking_container)
                total_reshuffles += int(not causes_no_additional_reshuffle(current_terminal, blocking_container, target_container_location, included_block_indices, container_labels))


            # retrieve target container
            current_terminal, _ = current_terminal.retrieve_container(target_container_location)
            removed_containers.add(target_container)

    return total_reshuffles


def causes_no_additional_reshuffle(terminal: Terminal,
                                   container: Container,
                                   to_exclude: StackTierLocation,
                                   included_block_indices: List[int],
                                   container_labels: dict) -> bool:
    # additional reshuffles is caused when
    # 1. a container departing earlier is present in the stack
    # 2. under the pyramid behind the stack no container is present that departs earlier than the specified container
    #   -> not strict a lowerbound anymore as the earlier container may be extracted from the other side
    valid_stacks = get_valid_stacks(terminal, to_exclude, included_block_indices, container_labels[container[0]])
    for stack, location in valid_stacks:
        if stack.height() == 0 or stack.min_container()[1] >= container[1]:
            return True
    return False










