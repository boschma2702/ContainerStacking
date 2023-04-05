from typing import List, Optional

from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events


class ValueFunctionApproximate:

    def value_approximate(self, iteration_number: int, t: int, terminal: Terminal, event: Events, corridor: Optional[List[int]]=None) -> float:
        """
        Function that returns the approximate value of the given terminal layout at time t (in iteration n).
        :param iteration_number:
        :param t:
        :param terminal:
        :param corridor: feature corridor (only check bays within the given corridor)
        :return:
        """
        raise NotImplementedError("Not Implemented")

    def on_iteration_done(self, iteration_number: int):
        raise NotImplementedError("Not Implemented")

    def on_sample_realization(self, n: int,
                              t: int,
                              previous_terminal: Terminal,
                              new_terminal: Terminal,
                              observed_value: float,
                              event: Events):
        """
        Function that gets called when a sample value is discovered.
        :param n: The current iteration of the ADP algorithm
        :param t: current time index
        :param previous_terminal: terminal layout at time t-1
        :param new_terminal: terminal layout at time t. It is reached by applying an action a to the previous_terminal
        :param observed_value: the observed value at time t (\hat{v}^n_t)
        :return: void
        """
        raise NotImplementedError("Not Implemented")




