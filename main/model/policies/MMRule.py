import math
from typing import Iterator

from main.model.adp.valuefunctions.features.MMRule import MM_store_container
from main.model.adp.valuefunctions.features.util.getBlocks import get_block_indices
from main.model.dataclass import Container, StackLocation

from main.model.dataclass.terminal import Terminal
from main.model.policies.baseHeuristic import Heuristic


class MMRule(Heuristic):

    def handle_inbound_container(self, terminal: Terminal, container: Container) -> Terminal:
        return MM_store_container(terminal, container, None, get_block_indices(terminal, None))

    def handle_reshuffles(self, initial_terminal: Terminal, target_container: Container,
                          blocking_containers: Iterator[Container], stack_index: StackLocation) -> Terminal:
        terminal = initial_terminal
        target_location = terminal.container_location(target_container)
        for blocking_container in blocking_containers:
            blocking_location = terminal.container_location(blocking_container)
            terminal, container = terminal.retrieve_container(blocking_location)
            assert container[0] == blocking_container[0]
            terminal = MM_store_container(terminal, blocking_container, target_location, get_block_indices(terminal, None))

        return terminal


