from typing import List

from main.model.dataclass import Container
from main.model.dataclass.block import Block
from main.model.dataclass.terminal import Terminal


def get_all_containers(terminal: Terminal, included_block_indices: List[int]) -> List[Container]:
    non_empty_stacks = [stack for i in included_block_indices for stack in terminal.blocks[i].stacks if stack.height()>0]
    return [container for stack in non_empty_stacks for container in stack.containers]
