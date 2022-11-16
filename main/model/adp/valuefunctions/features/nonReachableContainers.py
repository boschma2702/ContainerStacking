from typing import Optional, List

from main.model.adp.valuefunctions.features.util.getBlocks import get_blocks
from main.model.dataclass.block import Block
from main.model.dataclass.outcomes import _reachable
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events


def non_reachable_containers(terminal: Terminal, event: Events, current_batch_number: int, corridor: Optional[List[int]]):
    total = 0
    for block in get_blocks(terminal, corridor):
        for stack_index in range(len(block.stacks)):
            if _reachable(block, stack_index):
                # if reachable, the topmost container can be retrieved
                total += max(0, block.stacks[stack_index].height()-1)
            else:
                # stack is not reachable, thus entire height is added
                total += block.stacks[stack_index].height()

    return total



# t = Terminal((
#             Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
#             Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
#             Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), False)
#         ), 4)
# print(non_reachable_containers(t, None, 0))
# print(non_reachable_containers(t.store_container((2,2), (1,1,-1)).store_container((2,3), (1,1,-1)).store_container((2,0), (1,1,-1)), None, 0))

