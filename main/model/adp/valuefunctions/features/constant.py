from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events


def constant(terminal: Terminal, event: Events, current_batch_number: int):
    return 1


def constant_variable(value):
    return lambda terminal, event, current_batch_number: value
