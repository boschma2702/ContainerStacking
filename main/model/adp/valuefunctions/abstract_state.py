from typing import Callable

from main.model.adp.stepsize import StepSize
from main.model.adp.valuefunctions.valueFunctionApproximation import ValueFunctionApproximate
from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events


class AbstractState(ValueFunctionApproximate):

    def __init__(self, step_size: StepSize, initial_estimator: Callable[[Terminal, Events, int], float]):
        self.states = {}
        self.step_size = step_size
        self.initial_estimator = initial_estimator

        self.approx_values = {}
        self.iteration_values = {}

    def value_approximate(self, iteration_number: int, t: int, terminal: Terminal, event: Events) -> float:
        return self.approx_values.get((t, terminal.abstract()), self.initial_estimator(terminal, event, t))

    def on_iteration_done(self, iteration_number: int):
        self.approx_values.update(self.iteration_values)
        self.iteration_values = {}

    def on_sample_realization(self, n: int,
                              t: int,
                              previous_terminal: Terminal,
                              new_terminal: Terminal,
                              observed_value: float,
                              event: Events):
        # key = (t, new_terminal.abstract())
        abstract_terminal = previous_terminal.abstract()
        key = (t, abstract_terminal)
        prev_approximation = self.approx_values.get(key, self.initial_estimator(abstract_terminal, event, t))
        alpha = self.step_size.alpha
        self.iteration_values[key] = (1 - alpha) * prev_approximation + alpha * observed_value

    @staticmethod
    def underestimate(termina: Terminal, event: Events, t: int) -> float:
        return 0
