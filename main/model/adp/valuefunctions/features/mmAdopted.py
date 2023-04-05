from typing import Optional, List

from main.model.adp.valuefunctions.features.MMRule import MM_rule
from main.model.adp.valuefunctions.features.util.validStacks import get_valid_stacks
from main.model.dataclass import StackLocation, Container
from main.model.dataclass.block import Block
from main.model.dataclass.outcomes import _reachable_right, _reachable_left
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal


def MM_adopted_rule(terminal: Terminal, included_block_indices: List[int], container_labels: dict) -> float:
    return MM_rule(terminal, included_block_indices, container_labels, MM_adopted_store_container)


def MM_adopted_store_container(terminal: Terminal,
                               container: Container,
                               to_exclude: Optional[StackLocation],
                               included_block_indices: List[int],
                               container_labels: dict) -> Terminal:
    container_label = container_labels.get(container[0])
    valid_stacks = get_valid_stacks(terminal, to_exclude, included_block_indices, container_label) #yields a stack that is not valid as it introduces a new blocking
    # try to pick a stack that cause no new reshuffles, disregarding empty stacks
    no_reshuffle_stacks = [(stack[0].min_container(), stack[1]) for stack in valid_stacks if stack[0].height() > 0
                           and stack[0].min_container()[1] > container[1]
                           and not potential_blocking(terminal, stack[1], container)]
    no_reshuffle_stacks.sort()
    if len(no_reshuffle_stacks) > 0:
        return terminal.store_container(no_reshuffle_stacks[0][1], container)

    # check if empty stacks are available
    empty_stacks = [stack_tuple for stack_tuple in valid_stacks if stack_tuple[0].height() == 0]
    if len(empty_stacks) > 0:
        return terminal.store_container(empty_stacks[0][1], container)

    # find least harmful stack by selecting the stack that has the latest first departing container
    least_harmful = [(stack[0].min_container(), stack[1]) for stack in valid_stacks]
    least_harmful.sort(reverse=True)
    return terminal.store_container(least_harmful[0][1], container)

def potential_blocking(terminal: Terminal, stack_location: StackLocation, current_container: Container):
    block: Block = terminal.block(stack_location[0])
    current_stack_index = stack_location[1]

    # check if containers below are departing earlier
    target_stack: Stack = block.stacks[current_stack_index]
    target_height = target_stack.height()
    for container in target_stack.containers:
        if container[1] <= current_container[1]:
            return True

    # if reachable from left then containers to right must be departing later than the current container (otherwise
    # potential blocking). Only containers below the diagonal needs to be checked
    if _reachable_left(block, current_stack_index):
        for i in range(current_stack_index, len(block.stacks)):
            distance = abs(current_stack_index - i)
            stack: Stack = block.stacks[i]
            for container in stack.containers[:target_height+distance]:
                if container[1] <= current_container[1]:
                    return True

    # same, but then for the left
    if _reachable_right(block, current_stack_index):
        for i in range(current_stack_index):
            distance = abs(current_stack_index - i)
            stack: Stack = block.stacks[i]
            for container in stack.containers[:target_height + distance]:
                if container[1] <= current_container[1]:
                    return True
    return False


# container = (5,5,-1)
# t = Terminal((Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),), 4)
# t = t.store_container((0,2), (6,6,-1))\
#     .store_container((0,3), (7,7,-1))\
#     .store_container((0,3), (1,8,-1))
# # valid_stacks = get_valid_stacks(t, None) #yields a stack that is not valid as it introduces a new blocking
# # # try to pick a stack that cause no new reshuffles, disregarding empty stacks
# # no_reshuffle_stacks = [(stack[0].min_container(), stack[1]) for stack in valid_stacks if stack[0].height() > 0
# #                        and stack[0].min_container()[1] > container[1]
# #                        and not potential_blocking(t, stack[1], container)]
# #
# #
# # print([stack[1] for stack in no_reshuffle_stacks])
# print(potential_blocking(t, (0,2), container))