from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, List, Optional, Dict

import immutables

from main.model.dataclass import tuple_long_replace, StackLocation, Container, StackTierLocation
from main.model.dataclass.block import Block
from main.model.dataclass.stack import Stack


@dataclass(order=True)
class Terminal:
    __slots__ = ['max_height', 'blocks', 'container_locations']
    max_height: int
    blocks: Tuple[Block, ...]
    container_locations: immutables.Map

    def __init__(self, blocks: Tuple[Block, ...], max_height: int, container_locations=immutables.Map()):
        self.blocks = blocks
        self.max_height = max_height
        self.container_locations = container_locations

    @classmethod
    def empty_single_stack_block(cls, nr_stacks, max_height) -> Terminal:
        return cls(tuple([Block.empty_single_stack() for i in range(nr_stacks)]), max_height)

    @classmethod
    def empty_bay(cls, nr_bays, max_height) -> Terminal:
        return cls(tuple([Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True) for i in range(nr_bays)]), max_height)

    @staticmethod
    def get_container_store_locations(blocks):
        m = immutables.Map()
        m_mutation = m.mutate()
        for block_index in range(len(blocks)):
            block = blocks[block_index]
            for stack_index in range(len(block.stacks)):
                stack = block.stacks[stack_index]
                for tier_index in range(len(stack.containers)):
                    container = stack.containers[tier_index]
                    m_mutation.set(container[0], (block_index, stack_index, tier_index))

        return m_mutation.finish()
    ########################################################################################
    # Basic abstract, store, retrieve, reshuffle and reveal operations
    ########################################################################################

    def abstract(self) -> Terminal:
        blocks = tuple(sorted([block.abstract() for block in self.blocks]))
        locations = Terminal.get_container_store_locations(blocks)
        return Terminal(blocks, self.max_height, locations)

    def store_container(self, location: StackLocation, container: Container) -> Terminal:
        block = self.blocks[location[0]]
        tier = block.stacks[location[1]].height()
        replacement_stack = block.store_container(location[1], container)
        blocks = tuple_long_replace(self.blocks, location[0], replacement_stack)
        stack_tier_location: StackTierLocation = (location[0], location[1], tier)
        new_container_locations = self.container_locations.set(container[0], stack_tier_location)
        return Terminal(blocks, self.max_height, new_container_locations)

    def retrieve_container(self, location: StackLocation) -> Tuple[Terminal, Container]:
        new_block, container = self.blocks[location[0]].retrieve_container(location[1])
        blocks = tuple_long_replace(self.blocks, location[0], new_block)
        new_container_locations = self.container_locations.delete(container[0])
        return Terminal(blocks, self.max_height, new_container_locations), container

    def reshuffle_container(self, from_location: StackLocation, to_location: StackLocation) -> Terminal:
        new_term, container = self.retrieve_container(from_location)
        return new_term.store_container(to_location, container)

    def reveal_order(self, containers: Tuple[Container, ...]):
        order_dict = dict([(containers[i][0], i + 1) for i in range(len(containers))])
        return Terminal(tuple([block.reveal_order(order_dict) for block in self.blocks]), self.max_height, self.container_locations)

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
        return self.container_locations[container[0]]

    def blocking_containers(self, stack_tier_location: StackTierLocation) \
            -> List[Container]:
        return self.blocks[stack_tier_location[0]].blocking_containers(stack_tier_location[1:])

    def __repr__(self):
        split = "*" * 20 + "\n"
        return """\n{split}\n{blocks}\n{split}\n""".format(split=split, blocks="**\n".join([str(block) for block in self.blocks]))

    def __eq__(self, other):
        return self.blocks == other.blocks

    def __hash__(self):
        return hash(self.blocks)

