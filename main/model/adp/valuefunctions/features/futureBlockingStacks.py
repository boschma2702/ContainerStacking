from typing import Tuple

from main.model.dataclass import Container
from main.model.dataclass.block import Block
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events


def future_blocking_stacks(terminal: Terminal, event: Events, current_batch_number: int):
    result = 0
    stacks = [stack for block in terminal.blocks for stack in block.stacks]
    inbound_batches = [(t, event.batch(t).containers) for t in range(len(event.batches)) if t > current_batch_number and event.batch(t).inbound]
    for stack in stacks:
        if stack_is_blocking_in_future(stack, inbound_batches):
            result += 1

    return result



def stack_is_blocking_in_future(stack: Stack, inbound_batches: Tuple[int, Tuple[Container, ...]]):
    for t, inbound_containers in inbound_batches:
        remaining_containers = [container for container in stack.containers if container[1] > t]
        if len(remaining_containers) == 0:
            return False
        for inbound_container in inbound_containers:
            for remaining_container in remaining_containers:
                if remaining_container[1] >= inbound_container[1]:
                    return True

    return False

# inbound_batches = (
#     (10, ((1,1,-1), (2,2,-1))),
# )
# print(stack_is_blocking_in_future(Stack(((10,10,-1),)), inbound_batches))
# future_blocking_stacks(None, Events.create([(1, 2), (), (3,4,5,6), (2, 3)]), 4)
# e = Events.create([(1, 2), (), (3,4,5,6), (2, 3)])
# t = Terminal((
#             Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
#             Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
#             Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), False)
#         ), 4)
# # print(future_blocking_stacks(t, e, 0))
# print(future_blocking_stacks(t.store_container((2,2), (10,10,-1)).store_container((2,2), (11,11,-1)), e, 0))