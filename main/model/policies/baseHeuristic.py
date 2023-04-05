from decimal import Decimal
from typing import Tuple, Iterator

from main.model.dataclass import StackLocation, Container

from main.model.batch.realizedBatch import RealizedBatch
from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events
from main.model.policies.policy import Policy


class Heuristic(Policy):

    def __init__(self, events: Events, initial_terminal: Terminal, container_labels: dict):
        super().__init__(events, initial_terminal, container_labels)
        self.cache = {}

    def handle_realized_inbound_batch(self, terminal: Terminal, realized_batch: RealizedBatch, batch_number: int, container_labels: dict) \
            -> Tuple[Terminal, int]:
        new_terminal = terminal
        for container in realized_batch.containers:
            new_terminal = self.handle_inbound_container(new_terminal, container, container_labels)
        return new_terminal, 0

    def handle_realized_outbound_batch(self, initial_terminal: Terminal, realized_batch: RealizedBatch, batch_number: int, container_labels: dict) \
            -> Tuple[Terminal, int]:
        terminal = initial_terminal
        reshuffles = 0
        for target_container in realized_batch.containers:
            # get position of container
            current_block, current_stack, current_tier = terminal.container_location(target_container)
            stack_location = (current_block, current_stack)
            # move blocking containers
            blocking_containers = terminal.blocking_containers((current_block, current_stack, current_tier))
            if len(blocking_containers) > 0:
                terminal = self.handle_reshuffles(terminal, target_container, blocking_containers, stack_location, container_labels)
                reshuffles += len(blocking_containers)

            terminal, container = terminal.retrieve_container(stack_location)
            assert container[0] == target_container[0]
        return terminal, reshuffles

    def handle_inbound_container(self, terminal: Terminal, container: Container, container_labels: dict) -> Terminal:
        """
        Abstract method that handles an inbound container according to the defined heuristic.
        :param terminal: The terminal in which the given container needs to be placed
        :param container: the container that needs to be placed in the given terminal
        :return: The new terminal state (after placing the given container)
        """
        raise NotImplementedError

    def handle_reshuffles(self, terminal: Terminal, target_container: Container,
                          blocking_containers: Iterator[Container], stack_index: StackLocation, container_labels: dict) -> Terminal:
        """
        Abstract method that handles reshuffles according to the defined heuristic.
        :param terminal: The terminal in which the reshuffles are taken place
        :param target_container: the container to be retrieved
        :param blocking_containers: the containers blocking the target container, in order of how they can be retrieved
        :param stack_index: The stack index of the target and blocking containers
        :return: The new terminal state after the reshuffles are handled.
        """
        raise NotImplementedError

    def calculate_expected_reshuffles(self):
        return self.__calculate(self.initial_terminal, 0)

    def __calculate(self, initial_terminal: Terminal, t: int = 0) -> Decimal:
        events = self.events
        if t == events.length():
            return Decimal(0)
        terminal = initial_terminal.abstract()

        # check if the instance is already solved
        if (t, terminal) in self.cache:
            return self.cache[(t, terminal)]

        current_batch = events.batch(t)
        # abstracted_terminal = initial_terminal.abstract()

        value = Decimal(0)
        permutations = current_batch.unique_permutations()
        for batch_realization in permutations:
            if not current_batch.inbound:
                terminal = initial_terminal.reveal_order(batch_realization).abstract()

            if current_batch.inbound:
                new_terminal, costs = self.handle_realized_inbound_batch(terminal, batch_realization, t, self.container_labels)
            else:
                new_terminal, costs = self.handle_realized_outbound_batch(terminal, batch_realization, t, self.container_labels)

            value = value + costs + self.__calculate(new_terminal, t + 1)

        # expected_value = value * (1.0 / len(permutations))
        expected_value = value / len(permutations)

        self.cache[(t, initial_terminal.abstract())] = expected_value

        return expected_value
