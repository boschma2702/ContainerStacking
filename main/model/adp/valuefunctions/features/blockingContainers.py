from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events


def blocking_containers(terminal: Terminal, event: Events, current_batch_number: int) -> float:
    return sum([stack.blocking_lowerbound for block in terminal.blocks for stack in block.stacks])

