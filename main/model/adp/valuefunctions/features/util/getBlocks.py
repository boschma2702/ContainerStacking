from typing import Optional, List

from main.model.dataclass.block import Block
from main.model.dataclass.terminal import Terminal


def get_blocks(terminal: Terminal, corridor: Optional[List[int]]) -> List[Block]:
    if corridor is None:
        return list(terminal.blocks)
    return [terminal.blocks[i] for i in corridor]


def get_block_indices(terminal: Terminal, corridor: Optional[List[int]]) -> List[int]:
    if corridor is None:
        return list(range(len(terminal.blocks)))
    return corridor
