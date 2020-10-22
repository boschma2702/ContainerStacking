from typing import List

from main.model.batch import RealizedBatch
from main.model.dataclass import Container
from main.model.dataclass.block import Block
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events
from main.model.events.realizedEvents import RealizedEvents


def future_blocking_containers(terminal: Terminal, event: Events, current_batch_number: int):
    stacks = [stack for block in terminal.blocks for stack in block.stacks if stack.height()>0]
    inbound_batches = [(t, event.batch(t).containers) for t in range(len(event.batches)) if
                       t > current_batch_number and event.batch(t).inbound]
    total = 0
    for t, containers in inbound_batches:
        for container in containers:
            if container_is_blocking_future(container, t, stacks):
                total += 1
    return total


def container_is_blocking_future(container: Container, t: int, stacks: List[Stack]):
    for stack in stacks:
        for remaining_container in stack.containers:
            if remaining_container[1] > t and remaining_container[1] <= container[1]:
                return True
    return False


# e = RealizedEvents((RealizedBatch(True, ((10,10,-1),(11,11,-1))),))
#
# t = Terminal((
#             Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
#             Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
#             Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), False)
#         ), 4)
# print(container_is_blocking_future((2,2,-1), 0, [Stack(((1,5,-1),))]))
# print(future_blocking_containers(t.store_container((0,0), (1,1,-1)).store_container((1,1), (2,2,-1)), e, -1))