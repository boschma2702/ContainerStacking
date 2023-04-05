from typing import Optional, List

from main.model.adp.valuefunctions.features.util.getBlocks import get_blocks
from main.model.dataclass.block import Block
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events


def batch_label_difference(terminal: Terminal, event: Events, current_batch_number: int, corridor: Optional[List[int]], container_labels: dict) -> float:
    blocks = get_blocks(terminal, corridor)
    return sum([block_batch_label_diff(block) for block in blocks])


def block_batch_label_diff(block: Block) -> float:
    return sum([stack_batch_label_diff(stack) for stack in block.stacks])


def stack_batch_label_diff(stack: Stack) -> float:
    diff = 0
    if stack.height() > 1:
        for i in range(1, stack.height()):
            diff += stack.containers[i-1][1] - stack.containers[i][1]
        return diff
    else:
        return 0

# t: Terminal = Terminal((
#     Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
# ), 4)
# c: List[Container] = [(i, i, -1) for i in range(10)]
# t2 = t.store_container((0,0), c[0]).store_container((0,3), c[1])
# print(batch_label_diff(t))
# print(batch_label_diff(t2))
# print(batch_label_diff(t2.store_container((0,0), c[3])))
