import math
from queue import PriorityQueue
import random
from typing import Tuple, Set, Optional, List
import bisect

from main.model.dataclass import Container, StackLocation, StackTierLocation

from main.model.batch.realizedBatch import RealizedBatch
from main.model.dataclass.block import Block
from main.model.dataclass.terminal import Terminal
from main.model.noSolutionError import NoSolutionError
from main.model.util.prioritizedItem import PrioritizedItem


def terminal_unique_outcomes(terminal: Terminal, batch: RealizedBatch, corridor_size: int, container_labels: dict) \
        -> Set[Tuple[Terminal, int]]:
    if batch.length() == 0:
        return {(terminal, 0)}
    if batch.inbound:
        return _unique_inbound_outcomes(terminal, batch, corridor_size, container_labels)
    else:
        t = terminal.reveal_order(batch.containers)
        return _unique_outbound_outcomes(t, batch, corridor_size, container_labels)


def _unique_inbound_outcomes(initial_terminal: Terminal, batch: RealizedBatch, corridor_size, container_labels: dict) \
        -> Set[Tuple[Terminal, int]]:
    q = PriorityQueue()
    q.put(PrioritizedItem((0, 0), initial_terminal))
    abstract_added = set()
    result = set()
    while not q.empty():
        item = q.get(block=False)
        (i, reshuffles) = item.priority
        i = -i
        terminal = item.item

        # check if this is end state
        if i == batch.length():
            result.add((terminal, reshuffles))
        else:
            # not yet explored, need to add children to queue
            current_container = batch.containers[i]
            store_outcomes = store_locations(terminal, current_container, None, corridor_size, container_labels)
            for new_term in store_outcomes:
                new_term_abstracted = new_term.abstract()
                if new_term_abstracted not in abstract_added:
                    new_i = i + 1
                    abstract_added.add(new_term_abstracted)
                    q.put(PrioritizedItem((-new_i, reshuffles), new_term))
    if len(result) == 0:
        raise NoSolutionError("Could not find suitable solutions for batch: {}\n terminal:\n{}".format(batch, initial_terminal))
    return result


def _unique_outbound_outcomes(initial_terminal: Terminal, batch: RealizedBatch, corridor_size: int,
                              container_labels: dict) -> Set[Tuple[Terminal, int]]:
    q = PriorityQueue()
    q.put(PrioritizedItem((0, 0), initial_terminal))
    abstract_added = set()
    result = set()
    min_reshuffles = math.inf
    while not q.empty():
        item = q.get(block=False)
        (i, reshuffles) = item.priority
        i = -i
        terminal = item.item

        # if reshuffles is bigger than the current min reshuffles, disregard this option
        if reshuffles > min_reshuffles:
            continue

        # check if this is end state
        if i == batch.length():
            min_reshuffles = reshuffles
            result.add((terminal, reshuffles))
        else:
            # not yet explored, need to add children to queue
            current_container = batch.containers[i]
            handling_outcomes, is_reshuffle = handle_outbound_container(terminal, current_container, corridor_size, container_labels)
            new_i = i + int(not is_reshuffle)
            new_reshuffles = reshuffles + int(is_reshuffle)
            for new_term in handling_outcomes:
                new_term_abstracted = new_term.abstract()
                if new_term_abstracted not in abstract_added:
                    abstract_added.add(new_term_abstracted)
                    q.put(PrioritizedItem((-new_i, new_reshuffles), new_term))
    if len(result) == 0:
        raise NoSolutionError("Could not find suitable solutions for batch: {}\n terminal:\n{}"
                              .format(batch, initial_terminal))
    return result


def handle_outbound_container(terminal: Terminal, container: Container, corridor_size: int, container_labels: dict) \
        -> Tuple[Set[Terminal], bool]:
    current_stack_tier_location = terminal.container_location(container)
    blocking_containers = terminal.blocking_containers(current_stack_tier_location)

    if len(blocking_containers) > 0:
        blocking_container_location = terminal.container_location(blocking_containers[0])
        term, blocking_container = terminal.retrieve_container(blocking_container_location[:2])
        reshuffle_outcomes = store_locations(term, blocking_container, current_stack_tier_location, corridor_size, container_labels)
        return reshuffle_outcomes, True
    else:
        new_terminal, retrieved_container = terminal.retrieve_container(current_stack_tier_location[:-1])
        return {new_terminal}, False


def store_locations(terminal: Terminal, container: Container,
                    exclude_target_stack_tier_location: Optional[StackTierLocation], corridor_size: int,
                    container_labels: dict) -> Set[Terminal]:
    result = set()
    blocks_visited = set()
    for block_index in corridor(terminal, exclude_target_stack_tier_location, corridor_size):
        block = terminal.blocks[block_index]
        if block not in blocks_visited:
            blocks_visited.add(block)
            if container_allowed_in_block(block, container_labels[container[0]]):
                for stack_index in range(len(block.stacks)):
                    stack_location = (block_index, stack_index)
                    # check if container may be placed in this location
                    if valid_store_location(terminal, stack_location, exclude_target_stack_tier_location):
                        new_term = terminal.store_container((block_index, stack_index), container)
                        result.add(new_term)

    return result


def container_allowed_in_block(block, container_label):
    return container_label == 0 or container_label == block.designated


def corridor(terminal: Terminal, exclude_target_stack_tier_location: Optional[StackTierLocation], corridor_size: int,
             container_label: int) -> List[int]:
    # only use corridor if size is set
    if corridor_size >= 0:
        # if label = 0, then all places are available, otherwise limit to block equal to label

        # get bay indices with correct label
        if container_label == 0:
            block_indici = [i for i in range(0, terminal.nr_blocks())]
        else:
            block_indici = [i for i in range(0, terminal.nr_blocks()) if terminal.block(i).designated == container_label]

        # check if corridor spans all blocks
        if corridor_size*2 + 1 >= len(block_indici):
            return block_indici

        corridor_middle = exclude_target_stack_tier_location[0]
        bay_index = corridor_middle if corridor_middle else random.randint(0, len(block_indici)-1)

        # corridor contains at least the 'starting point'
        corridor = [bay_index]

        if bay_index not in block_indici: bisect.insort(block_indici, bay_index)

        # add corridor_size indici smaller in block_indici to corridor
        bay_index_index = bisect.bisect(block_indici, bay_index) - 1

        for i in range(1, corridor_size+1):
            up = (bay_index_index + i) % len(block_indici)
            down = (bay_index_index - i) % len(block_indici)
            corridor.append(block_indici[up])
            corridor.append(block_indici[down])

        return corridor

    return list(range(terminal.nr_blocks()))


def valid_store_location(terminal: Terminal,
                         stack_location: StackLocation,
                         target_stack_tier_location: Optional[StackTierLocation]):
    # stack is not full
    max_stack_height = terminal.max_height
    non_full = terminal.stack_height(stack_location) < max_stack_height

    if not non_full:
        return False

    # a container may not be stored when the target container is located in the same stack
    if target_stack_tier_location is not None and stack_location == target_stack_tier_location[:-1]:
        return False

    # if bay is empty, stack_location must be in the middle, otherwise must be against a neighbouring
    if not correct_bay_location(terminal, stack_location):
        return False

    # stack must be reachable
    if not _reachable(terminal.blocks[stack_location[0]], stack_location[1]):
        return False

    # if target stack tier is supplied, it is not allowed to store a container below the diagonal of the target container
    return below_diagonal(terminal, stack_location, target_stack_tier_location)


def correct_bay_location(terminal: Terminal, stack_location: StackLocation):
    block = terminal.blocks[stack_location[0]]
    if block.two_way:
        return _correct_bay_location_two_way(block, stack_location)
    else:
        return _correct_bay_location_one_way(block, stack_location)


def _correct_bay_location_one_way(block: Block, stack_location: StackLocation):
    nr_stacks = len(block.stacks)
    # if bay is empty, must be placed all the way to the right
    if all_empty_in_range(block, range(nr_stacks)):
        return stack_location[1] == nr_stacks-1

    # if stack already has a container placed on it, it is allowed to build on top of it
    if block.stacks[stack_location[1]].height() > 0:
        return True

    # if there exist an empty stack to the right of the given stack, it is not a valid position
    if exist_empty_in_range(block, range(stack_location[1]+1)):
        return False

    # if above checks hold, it is a valid location according to this rule
    return True


def _correct_bay_location_two_way(block: Block, stack_location: StackLocation):
    nr_stacks = len(block.stacks)
    stack_index = stack_location[1]
    # if bay is emtpy, must be placed in the middle
    if all_empty_in_range(block, range(nr_stacks)):
        return nr_stacks <= 2 or len(block.stacks) // 2 == stack_location[1]

    # if stack already has a container placed on it, it is allowed to build on top of it
    if block.stacks[stack_index].height() > 0:
        return True

    # direct neighbour stack must not be empty and other side must all be empty
    # right neighbour, left empty:
    right_neighbour = has_container(block, stack_index+1) and all_empty_in_range(block, range(stack_index))

    # left neighbour, right empty:
    return right_neighbour or (has_container(block, stack_index-1) and all_empty_in_range(block, range(stack_index+1, nr_stacks)))


def below_diagonal(terminal: Terminal, stack_location: StackLocation, target_stack_tier: Optional[StackTierLocation]):
    # if target stack tier is None, the check on diagonal is not needed
    if target_stack_tier is None:
        return True

    # if bays are different, the check on diagonal is not needed
    if stack_location[0] != target_stack_tier[0]:
        return True

    block = terminal.blocks[stack_location[0]]
    target_tier = target_stack_tier[2]
    target_stack_index = target_stack_tier[1]
    stack_index = stack_location[1]
    stack_distance = abs(target_stack_index - stack_index)

    if stack_index < target_stack_index:
        # target is on the right, thus needs to be below diagonal
        diagonal = (block.stacks[stack_index].height()) < (target_tier - stack_distance) and _reachable_left(block, stack_index)
    else:
        # target is on the left, thus needs to be above diagonal
        diagonal = (block.stacks[stack_index].height()) > (target_tier + stack_distance) and _reachable_left(block, stack_index)

    if block.two_way and not diagonal:
        if stack_index < target_stack_index:
            # target is on the left, thus needs to be above diagonal
            diagonal = (block.stacks[stack_index].height()) > (target_tier + stack_distance) and _reachable_right(block, stack_index)
        else:
            # target is on the right, thus needs to be below diagonal
            diagonal = (block.stacks[stack_index].height()) < (target_tier - stack_distance) and _reachable_right(block, stack_index)

    return diagonal



def exist_empty_in_range(block: Block, iterator):
    for stack_index in iterator:
        stack = block.stacks[stack_index]
        if stack.height() == 0:
            return True
    return False


def all_empty_in_range(block: Block, iterator):
    for stack_index in iterator:
        stack = block.stacks[stack_index]
        if stack.height() > 0:
            return False
    return True


def has_container(block: Block, stack_index: int):
    in_range = 0 <= stack_index < len(block.stacks)
    return in_range and block.stacks[stack_index].height() > 0


def _reachable_right(block: Block, stack_location: int):
    return block.two_way and _reachable_base(block, stack_location, range(stack_location + 1, len(block.stacks)))


def _reachable_left(block: Block, stack_location: int):
    return _reachable_base(block, stack_location, range(stack_location))


def _reachable_base(block: Block, stack_location: int, iterator):
    stack_height = block.stacks[stack_location].height()
    for i in iterator:
        stack_distance = abs(stack_location - i)
        i_height = block.stacks[i].height()
        below_diagonal = i_height <= (stack_height - stack_distance) or i_height == 0
        if not below_diagonal:
            return False
    return True


def _reachable(block: Block, stack_location: int):
    stack_height = block.stacks[stack_location].height()
    reachable = True
    for i in range(stack_location):
        stack_distance = stack_location - i
        i_height = block.stacks[i].height()
        below_diagonal = i_height <= (stack_height - stack_distance) or i_height == 0
        if not below_diagonal:
            reachable = False
            break

    if block.two_way and not reachable:
        reachable = True
        for i in range(stack_location + 1, len(block.stacks)):
            stack_distance = i - stack_location
            i_height = block.stacks[i].height()
            below_diagonal = i_height <= (stack_height - stack_distance) or i_height == 0
            if not below_diagonal:
                reachable = False
                break
    return reachable
