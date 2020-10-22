from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events


def unordered_stacks(terminal: Terminal, event: Events, current_batch_number: int) -> float:
    """
    Counts the number of stacks which are not strictly ordered. This means that in retrieving the containers of this
    stack in order a reshuffle (might, due to batch labels) occur.
    :param terminal:
    :return:
    """
    return sum([sum([stack.blocking_lowerbound > 0 for stack in block.stacks]) for block in terminal.blocks])
