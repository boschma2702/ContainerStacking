from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, List, Optional

from main.model.dataclass import tuple_short_replace, Container, StackTierLocation, StackLocation
from main.model.dataclass.stack import Stack


@dataclass(order=True)
class Block:
    __slots__ = ['two_way', 'stacks', 'designated']
    two_way: bool
    stacks: Tuple[Stack, ...]
    designated: int

    def __init__(self, stacks: Tuple[Stack, ...], two_way: bool, designated: Optional[int] = 0):
        self.stacks = stacks
        self.two_way = two_way
        self.designated = designated

    @classmethod
    def empty_single_stack(cls) -> Block:
        return cls((Stack.empty(),), False)

    def abstract(self) -> Block:
        stacks = tuple([stack.abstract() for stack in self.stacks])
        if self.two_way and len(self.stacks) > 1:
            return Block(min(stacks, self.stacks[::-1]), self.two_way, self.designated)
        return Block(stacks, self.two_way, self.designated)

    def store_container(self, stack_index: int, container: Container) -> Block:
        return Block(tuple_short_replace(
                self.stacks,
                stack_index,
                self.stacks[stack_index].store_container(container)
            ),
            self.two_way,
            self.designated
        )

    def retrieve_container(self, stack_index: int) -> Tuple[Block, Container]:
        stack, container = self.stacks[stack_index].retrieve_container()
        new_stacks: Tuple[Stack] = tuple_short_replace(self.stacks, stack_index, stack)
        return Block(new_stacks, self.two_way, self.designated), container

    def reveal_order(self, order_dict: dict) -> Block:
        return Block(tuple([stack.reveal_order(order_dict) for stack in self.stacks]), self.two_way, self.designated)

    def blocking_containers(self, stack_location: StackLocation) -> List[Container]:
        """
        Returns the blocking containers for the given stack tier location. This blocking respects the reachstacker
        capabilities. It is assumed that a reach stacker can only extract containers whenever the neighbouring stacks
        are at least one lower (i.e. from the given stack tier location, containers are allowed to remain on the
        diagonal down, everything above is assumed to be blocking.

        If the block can be approached from both sides (i.e. two_sides == True), then this function checks which side
        returns the least number of containers that need to be reshuffled.
        :param stack_tier_location: (stack_index, height)
        :return: A list of blocking containers in order of the way they can be retrieved. To reduce the number of
        possibilities and simplicity, it is assumed that containers are reshuffled starting from all blocking containers
        in the most left (or right) stack towards all blocking containers in the target stack.
        """
        stack_index, tier_index = stack_location
        neighbour_above = []
        for neighbour_index in range(stack_index):
            allowed_tier = tier_index - (stack_index-neighbour_index)
            neighbour_above.extend(reversed(self.stacks[neighbour_index].containers_above(allowed_tier)))

        other_way = []
        if self.two_way and len(neighbour_above) > 0:
            for neighbour_index in range(len(self.stacks)-1, stack_index, -1):
                allowed_tier = tier_index - (neighbour_index - stack_index)
                other_way.extend(reversed(self.stacks[neighbour_index].containers_above(allowed_tier)))

            if len(other_way) < len(neighbour_above):
                other_way.extend(reversed(self.stacks[stack_index].containers_above(tier_index)))
                return other_way

        neighbour_above.extend(reversed(self.stacks[stack_index].containers_above(tier_index)))
        return neighbour_above

    # def designated_label(self):
    #     """
    #     Returns the designated label. Label of 0 indicates a non-label (i.e. equivalent to a block that has no label).
    #     Designated means that certain contains are only allowed to stay at these blocks, rather than all blocks. This
    #     does mean that a container without a label is still allowed to be stored at a block with a label.
    #     """
    #     return self.designated

    # @lru_cache(1)
    def __hash__(self):
        return hash((self.two_way, self.stacks))

    def __repr__(self):
        return str(self.designated)+"\n"+"\n".join([str(stack) for stack in self.stacks])

