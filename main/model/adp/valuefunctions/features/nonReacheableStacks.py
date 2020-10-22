from main.model.dataclass.block import Block
from main.model.dataclass.outcomes import _reachable
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events


def non_reachable_stacks(terminal: Terminal, event: Events, current_batch_number: int):
    return sum([not _reachable(block, stack_index) for block in terminal.blocks for stack_index in range(len(block.stacks))])


# t = Terminal((
#             Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
#             Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
#             Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), False)
#         ), 4)
# print(non_reachable_stacks(t, None, 0))
# print(non_reachable_stacks(t.store_container((2,2), (1,1,-1)), None, 0))