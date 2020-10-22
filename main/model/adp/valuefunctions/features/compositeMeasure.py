from typing import Optional, Set, List, Tuple

from main.model.adp.valuefunctions.features.MMRule import MM_rule
from main.model.adp.valuefunctions.features.mmAdopted import MM_adopted_rule
from main.model.adp.valuefunctions.features.util.getAllContainers import get_all_containers
from main.model.adp.valuefunctions.features.util.validStacks import get_valid_stacks
from main.model.dataclass import StackLocation, Container, StackTierLocation
from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events

ALPHA = 0.65


def composite_adopted_measure(terminal: Terminal, event: Events, current_batch_number: int):
    mmrule_score = MM_adopted_rule(terminal)
    crl_score = crl(terminal)
    return ALPHA * mmrule_score + (1-ALPHA) * crl_score


def composite_measure(terminal: Terminal, event: Events, current_batch_number: int):
    mmrule_score = MM_rule(terminal)
    crl_score = crl(terminal)
    return ALPHA * mmrule_score + (1-ALPHA) * crl_score


def crl(terminal: Terminal) -> float:
    # determine order of container retrieval
    retrieval_order = get_all_containers(terminal)
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
                total_reshuffles += int(not causes_no_additional_reshuffle(current_terminal, blocking_container, target_container_location))


            # retrieve target container
            current_terminal, _ = current_terminal.retrieve_container(target_container_location)
            removed_containers.add(target_container)

    return total_reshuffles


def causes_no_additional_reshuffle(terminal: Terminal, container: Container, to_exclude: StackTierLocation) -> bool:
    # additional reshuffles is caused when
    # 1. a container departing earlier is present in the stack
    # 2. under the pyramid behind the stack no container is present that departs earlier than the specified container
    #   -> not strict a lowerbound anymore as the earlier container may be extracted from the other side
    valid_stacks = get_valid_stacks(terminal, to_exclude)
    for stack, location in valid_stacks:
        if stack.height() == 0 or stack.min_container()[1] >= container[1]:
            return True
    return False


# def earlier_departing_in_pyramid_behind(terminal: Terminal, stack: Stack, location: StackLocation, container: Container):
#     block = terminal.blocks[location[0]]
#     stack_height = stack.height()
#     # check from left
#     if _reachable_left(block, location[1]):
#         for i in range(location[1], len(block.stacks)):
#             neighbour_stack: Stack = block.stacks[i]
#             diff = i - location[1]
#             for h in range(min(neighbour_stack.height(), stack_height + diff + 1)):
#                 if neighbour_stack.containers[h][1] <= container[1]:
#                     # this position causes an additional reshuffle
#                     return True
#     # check from right
#     if block.two_way and _reachable_right(block, location[1]):
#         for i in range(location[1], -1, -1):
#             neighbour_stack: Stack = block.stacks[i]
#             diff = i - location[1]
#             for h in range(min(neighbour_stack.height(), stack_height + diff + 1)):
#                 if neighbour_stack.containers[h][1] <= container[1]:
#                     # this position causes an additional reshuffle
#                     return True
#     return False

# t = Terminal.empty_single_stack_block(5,4).store_container((0,0), (1,1,-1)).store_container((1,0), (2,2,-1)).store_container((0,0), (3,3,-1))
# t = Terminal(
#         (
#             Block(
#                 (
#                     Stack(((6, 6, -1), (2, 1, -1), (1, 1, -1), (3, 3, -1),)),
#                     Stack(((4, 4, -1), (5, 3, -1), (8, 3, -1))),
#                 ), True
#             ),
#             Block(
#                 (
#                     Stack(((10,2,-1),)),
#                 ), False
#             )
#         ), 4
#     )
# print(MM_rule(t))
# print(crl(t))




# failing test instance
# t = Terminal((
#             Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
#             Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
#             Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True)
#         ), 4)
#
# t = t.store_container((0,0), (1,28,-1))\
#     .store_container((0,1), (12,11,-1))\
#     .store_container((0,2), (6,13,-1)).store_container((0,2), (3,46,-1))
#
# t = t.store_container((1,2),(7,2,-1)).store_container((1,2), (20,14,-1))
# print(MM_rule(t))

# target container: (20, 14, -1), retrieval_order: [(7, 2, -1), (12, 11, -1), (6, 13, -1), (20, 14, -1), (1, 28, -1), (3, 46, -1)]
# start terminal:
# ********************
# -28_?(1)
# -11_?(12)
# -13_?(6)∣46_?(3)
# -
# -
# **
# -
# -
# -2_?(7)∣14_?(20)
# -
# -
# **
# -
# -
# -
# -
# -
# ********************
# old terminal:
# ********************
# -
# -
# -
# -28_?(1)
# -28_?(1)
# **
# -
# -
# -46_?(3)
# -
# -
# **
# -
# -
# -
# -
# -
# ********************
# terminal:
# ********************
# -
# -
# -
# -28_?(1)
# -28_?(1)
# **
# -
# -
# -46_?(3)
# -
# -
# **
# -
# -
# -
# -
# -
# ********************












