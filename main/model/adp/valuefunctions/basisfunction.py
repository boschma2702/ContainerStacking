from typing import Callable, List, Optional

import numpy

from main.model.adp.fileWriter import FileWriter
from main.model.adp.valuefunctions.valueFunctionApproximation import ValueFunctionApproximate
from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events


class BasisFunction(ValueFunctionApproximate):

    def value_approximate(self, n: int, t: int, terminal: Terminal, event: Events, corridor: Optional[List[int]] = None) -> float:
        # weights = self.weights[n].get(t, self.init_weights)
        weights = self.get_last_known(self.weights, self.init_weights, n, t)
        result = numpy.sum(weights.T * self.feature_evaluation(terminal, event, t, corridor))
        return result

    def on_iteration_done(self, iteration_number: int):
        # add new hash for iteration_number + 1
        self.weights[iteration_number + 1] = {}
        self.B[iteration_number + 1] = {}
        # weights are updated as soon as they are observed, so no need to do it here

        # write the weights to a weights file
        if self.file_writer:
            s = "---------- Iteration {} ----------\n".format(iteration_number)
            for t in sorted(self.weights[iteration_number]):
                s += "{}: {}\n".format(t, ", ".join(["{:.20f}".format(w) for w in self.weights[iteration_number][t].T[0]]))
            self.file_writer.write_to_instance_folder(FileWriter.FILE_WEIGHTS, s)


    def on_sample_realization(self, n: int, t: int, previous_terminal: Terminal, new_terminal: Terminal,
                              observed_value: float, event: Events):
        # sample is observed, calculate the new weights to update them
        value_estimate = self.value_approximate(n - 1, t, previous_terminal, event)
        error = value_estimate - observed_value

        # convert to correct size (numpy qwerks)
        feature_evaluation = self.feature_evaluation(previous_terminal, event, t, None)
        feature_evaluation = numpy.atleast_2d(feature_evaluation).T

        # previous_weights = self.weights[n - 1].get(t, self.get_last_known_weight(n-1, t))
        previous_weights = self.get_last_known(self.weights, self.init_weights, n-1, t)
        # previous_B_n = self.B[n - 1].get(t, self.init_B)
        previous_B_n = self.get_last_known(self.B, self.init_B, n-1, t)
        gamma_n = self.alpha(n) + feature_evaluation.T @ previous_B_n @ feature_evaluation
        H_n = (1 / gamma_n) * previous_B_n

        update_weights = (H_n @ feature_evaluation * error)
        weights_n_t = previous_weights - update_weights
        self.weights[n][t] = weights_n_t

        # update B^n
        matrix_mul = previous_B_n @ feature_evaluation @ feature_evaluation.T @ previous_B_n
        B_n = (1 / self.alpha(n)) * (previous_B_n - (1 / gamma_n) * matrix_mul)
        self.B[n][t] = B_n

    def feature_evaluation(self, state, event: Events, t: int, corridor: Optional[List[int]]):
        # Calculates \phi
        return numpy.array([f(state, event, t, corridor) for f in self.feature_functions])

    def alpha(self, n) -> float:
        # calculate \alpha_n
        return 1 - (self.delta / n)

    def __init__(self, feature_functions: List[Callable[[Terminal, Events, int, Optional[List[int]]], float]],
                 init_weight, epsilon=0.1, delta=0.5, file_writer: Optional[FileWriter] = None):
        self.file_writer = file_writer
        # small constant to initialize Bn. This initialization works well when the number of observations is large
        self.epsilon = epsilon
        # constant used to determine alpha^n. The value of alpha determines the weight on prior observations (lower
        # alpha means lower weight).
        self.delta = delta

        # using dicts
        self.feature_functions = feature_functions
        if type(init_weight) is float:
            self.init_weights = numpy.array([[init_weight for i in range(len(feature_functions))]]).T
            # self.weights = {1: numpy.array([init_weight for i in range(len(feature_functions))])}
        elif type(init_weight) is list:
            assert len(init_weight) == len(feature_functions)
            self.init_weights = numpy.array([init_weight]).T
            # self.weights = {1: numpy.array(init_weight)}
        else:
            raise ValueError("Unsupported weight type")

        self.init_B = self.epsilon * numpy.identity(len(feature_functions))
        self.weights = {0: {}, 1: {}}
        self.B = {0: {}, 1: {}}
        self.observations = {}

    def get_last_known(self, dictionary, default, n, t):
        while n > 0:
            if t in dictionary[n]:
                return dictionary[n][t]
            n = n - 1
        dictionary[n][t] = default
        return default
        # raise RuntimeError("Could not find last known in dictionary for n: {} t: {}".format(n, t))





# Test for convergence
# fs = [lambda x: 100.0, lambda x: 150.0]
# b = BasisFunction(fs, 1.0, 0.1, 0)
# for n in range(1, 31):
#     print("{}. value {:20} \t\t\t\t\t{}".format(n-1, b.value_approximate(n-1, 1, None), b.weights[n-1].get(1, b.init_weights).T))
#     b.on_sample_realization(n, 1, None, None, 2)
#     b.on_iteration_done(n)
