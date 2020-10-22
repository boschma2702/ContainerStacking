from statistics import mean

from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events


def average_stack_height(terminal: Terminal, event: Events, current_batch_number: int) -> float:
    """
    Calculates the average stack height of non empty stacks
    :param terminal:
    :return:
    """
    l = [
        stack.height() for block in terminal.blocks for stack in block.stacks if stack.height() > 0
    ]
    if len(l) == 0:
        return 0
    return mean(l)

# t = Terminal.empty_single_stack_block(10, 4)
# print(average_stack_height(t.store_container((0,0), (1,1,-1))))
