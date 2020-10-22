from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, List, Optional

from main.model.dataclass import tuple_long_replace, StackLocation, Container, StackTierLocation
from main.model.dataclass.block import Block
from main.model.dataclass.stack import Stack


@dataclass(order=True)
class Terminal:
    __slots__ = ['max_height', 'blocks']
    max_height: int
    blocks: Tuple[Block, ...]

    # cache_hash: Any

    def __init__(self, blocks: Tuple[Block, ...], max_height: int):
        self.blocks = blocks
        self.max_height = max_height

    @classmethod
    def empty_single_stack_block(cls, nr_stacks, max_height) -> Terminal:
        return cls(tuple([Block.empty_single_stack() for i in range(nr_stacks)]), max_height)

    @classmethod
    def empty_bay(cls, nr_bays, max_height) -> Terminal:
        return cls(tuple([Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True) for i in range(nr_bays)]), max_height)

    ########################################################################################
    # Basic abstract, store, retrieve, reshuffle and reveal operations
    ########################################################################################

    def abstract(self) -> Terminal:
        return Terminal(tuple(sorted([block.abstract() for block in self.blocks])), self.max_height)

    def store_container(self, location: StackLocation, container: Container) -> Terminal:
        replacement = self.blocks[location[0]].store_container(location[1], container)
        blocks = tuple_long_replace(self.blocks, location[0], replacement)
        return Terminal(blocks, self.max_height)

    def retrieve_container(self, location: StackLocation) -> Tuple[Terminal, Container]:
        new_block, container = self.blocks[location[0]].retrieve_container(location[1])
        blocks = tuple_long_replace(self.blocks, location[0], new_block)
        return Terminal(blocks, self.max_height), container

    def reshuffle_container(self, from_location: StackLocation, to_location: StackLocation) -> Terminal:
        new_term, container = self.retrieve_container(from_location)
        return new_term.store_container(to_location, container)

    def reveal_order(self, containers: Tuple[Container, ...]):
        order_dict = dict([(containers[i][0], i + 1) for i in range(len(containers))])
        return Terminal(tuple([block.reveal_order(order_dict) for block in self.blocks]), self.max_height)

    ########################################################################################
    # Misc util operators
    ########################################################################################

    def nr_blocks(self) -> int:
        return len(self.blocks)

    def block(self, i: int) -> Block:
        return self.blocks[i]

    def stack_height(self, stack_location: StackLocation) -> int:
        return len(self.blocks[stack_location[0]].stacks[stack_location[1]].containers)

    def container_location(self, container: Container):
        container_id = container[0]
        for block_index in range(len(self.blocks)):
            block = self.blocks[block_index]
            for stack_index in range(len(block.stacks)):
                stack = block.stacks[stack_index]
                for tier_index in range(len(stack.containers)):
                    if container_id == stack.containers[tier_index][0]:
                        return block_index, stack_index, tier_index
        raise RuntimeError("Could not find given container")

    # def containers_above(self, stack_tier_location: StackTierLocation) -> Tuple[Container, ...]:
    #     stack = self.blocks[stack_tier_location[0]].stacks[stack_tier_location[1]]
    #     return stack.containers[stack_tier_location[2] + 1:]

    def blocking_containers(self, stack_tier_location: StackTierLocation) \
            -> List[Container]:
        return self.blocks[stack_tier_location[0]].blocking_containers(stack_tier_location[1:])

    def __repr__(self):
        split = "*" * 20 + "\n"
        return """\n{split}\n{blocks}\n{split}\n""".format(split=split, blocks="**\n".join([str(block) for block in self.blocks]))

    def __hash__(self):
        return hash(self.blocks)

