from typing import Optional, List

from main.model.adp.valuefunctions.features.util.getBlocks import get_blocks
from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events


def blocking_containers(terminal: Terminal, event: Events, current_batch_number: int, corridor: Optional[List[int]], container_labels: dict) -> float:
    blocks = get_blocks(terminal, corridor)
    return sum([stack.blocking_lowerbound for block in blocks for stack in block.stacks])

