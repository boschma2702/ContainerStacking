from typing import List

from main.model.dataclass import Container
from main.model.dataclass.terminal import Terminal


def get_all_containers(terminal: Terminal) -> List[Container]:
    non_empty_stacks = [stack for block in terminal.blocks for stack in block.stacks if stack.height()>0]
    return [container for stack in non_empty_stacks for container in stack.containers]
