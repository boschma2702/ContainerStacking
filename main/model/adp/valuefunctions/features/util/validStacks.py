from typing import Optional, List, Tuple

from main.model.dataclass import StackTierLocation, StackLocation
from main.model.dataclass.block import Block
from main.model.dataclass.outcomes import valid_store_location
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal


def get_valid_stacks(terminal: Terminal, to_exclude: Optional[StackTierLocation], included_blocks_indices: List[int]) -> List[Tuple[Stack, StackLocation]]:
    available_stacks = []
    for block_index in included_blocks_indices:
        block = terminal.blocks[block_index]
        for stack_index in range(len(block.stacks)):
            stack_location = (block_index, stack_index)
            if valid_store_location(terminal, stack_location, to_exclude):
                stack = block.stacks[stack_index]
                available_stacks.append((stack, (block_index, stack_index)))
    return available_stacks
