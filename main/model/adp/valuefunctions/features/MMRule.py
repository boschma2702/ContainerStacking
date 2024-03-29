from typing import Optional, List, Callable

from main.model.adp.valuefunctions.features.util.getAllContainers import get_all_containers
from main.model.adp.valuefunctions.features.util.validStacks import get_valid_stacks
from main.model.dataclass import Container, StackLocation
from main.model.dataclass.terminal import Terminal


def MM_store_container(terminal: Terminal, container: Container, to_exclude: Optional[StackLocation]) -> Terminal:
    valid_stacks = get_valid_stacks(terminal, to_exclude) #yields a stack that is not valid as it introduces a new blocking
    # try to pick a stack that cause no new reshuffles, disregarding empty stacks
    no_reshuffle_stacks = [(stack[0].min_container(), stack[1]) for stack in valid_stacks if stack[0].height() > 0 and stack[0].min_container()[1] > container[1]]
    no_reshuffle_stacks.sort()
    if len(no_reshuffle_stacks) > 0:
        return terminal.store_container(no_reshuffle_stacks[0][1], container)

    # check if empty stacks are available
    empty_stacks = [stack_tuple for stack_tuple in valid_stacks if stack_tuple[0].height() == 0]
    if len(empty_stacks) > 0:
        return terminal.store_container(empty_stacks[0][1], container)

    # find least harmful stack by selecting the stack that has the latest first departing container
    least_harmful = [(stack[0].min_container(), stack[1]) for stack in valid_stacks]
    least_harmful.sort(reverse=True)
    return terminal.store_container(least_harmful[0][1], container)


def MM_rule(terminal: Terminal, store_container_func: Callable[[Terminal, Container, Optional[StackLocation]], Terminal] = MM_store_container) -> float:
    # determine order of container retrieval
    retrieval_order = get_all_containers(terminal)
    retrieval_order.sort(key=lambda x: x[1:])

    current_terminal = terminal
    total_reshuffles = 0
    previous_terminal = None
    # handle each container
    for target_container in retrieval_order:
        try:
            target_container_location = current_terminal.container_location(target_container)
            previous_terminal = current_terminal
            # handle blocking containers
            blocking_containers: List[Container] = current_terminal.blocking_containers(target_container_location)
            total_reshuffles += len(blocking_containers)
            for blocking_container in blocking_containers:
                blocking_location = current_terminal.container_location(blocking_container)
                current_terminal, _ = current_terminal.retrieve_container(blocking_location)
                current_terminal = store_container_func(current_terminal, blocking_container, target_container_location)

            # retrieve target container
            current_terminal, _ = current_terminal.retrieve_container(target_container_location)
        except RuntimeError:
            print("target container: {}, retrieval order: {}".format(target_container, retrieval_order))
            print("start terminal:\n{}".format(terminal))
            print("previous terminal:\n{}".format(previous_terminal))
            print("current terminal:\n{}".format(current_terminal))
            raise RuntimeError

    return total_reshuffles



