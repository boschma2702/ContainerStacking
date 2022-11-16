import math
import random
from statistics import mean, stdev
from typing import Tuple, Set

import numpy as np

from main.model.adp.valuefunctions.valueFunctionApproximation import ValueFunctionApproximate
from main.model.batch.realizedBatch import RealizedBatch
from main.model.dataclass.optimizedOutcomes import terminal_optimized_outcome
from main.model.dataclass.outcomes import terminal_unique_outcomes
from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events
from main.model.events.realizedEvents import RealizedEvents
from main.model.noSolutionError import NoSolutionError
from main.model.policies.policy import Policy


class ADP(Policy):
    NO_SOLUTION_COST = 9999999999999999999

    def __init__(self,
                 events: Events,
                 initial_terminal: Terminal,
                 single: bool,
                 epsilon: float,
                 value_function_approx: ValueFunctionApproximate,
                 number_sample_iterations=250,
                 discount_factor=1,
                 evaluate: bool = False,
                 every_th_iteration=10,
                 evaluation_samples=1000,
                 problem_instance=0,
                 use_optimized_outcomes=False,
                 corridor_size: int = -1,
                 corridor_feature: int = -1
                 ):
        super().__init__(events, initial_terminal)
        # ADP settings
        self.single = single
        # self.epsilon = 0.25
        self.epsilon = epsilon
        self.value_function_approximator = value_function_approx
        self.discount_factor = discount_factor
        self.n = 1
        self.N = number_sample_iterations

        self.use_optimized_outcomes = use_optimized_outcomes
        self.corridor_size = corridor_size
        self.corridor_feature = corridor_feature

        # evaluation settings
        self.evaluate = evaluate
        if evaluate:
            self.events.reset()
        self.every_th_iteration = every_th_iteration
        self.evaluation_samples = evaluation_samples
        self.evaluation_results = {}
        self.problem_instance = problem_instance

        self.determine_approximate_values()

    ########################################################################################
    # Policy evaluation code
    ########################################################################################
    def handle_realized_inbound_batch(self, terminal: Terminal, realized_batch: RealizedBatch,
                                      batch_number: int) -> Tuple[Terminal, int]:
        if not self.use_optimized_outcomes:
            return self._best_choice(terminal_unique_outcomes(terminal, realized_batch, self.corridor_size),
                                     batch_number)
        else:
            return terminal_optimized_outcome(terminal, realized_batch, self.value_function_approximator, self.n,
                                              batch_number, self.events, self.corridor_size, self.corridor_feature,
                                              False)[:-1]

    def handle_realized_outbound_batch(self, terminal: Terminal, realized_batch: RealizedBatch,
                                       batch_number: int) -> Tuple[Terminal, int]:
        if not self.use_optimized_outcomes:
            return self._best_choice(terminal_unique_outcomes(terminal, realized_batch, self.corridor_size),
                                     batch_number)
        else:
            return terminal_optimized_outcome(terminal, realized_batch, self.value_function_approximator, self.n,
                                              batch_number, self.events, self.corridor_size, self.corridor_feature,
                                              False)[:-1]

    def _best_choice(self, outcomes: Set[Tuple[Terminal, int]], current_batch_number: int) \
            -> Tuple[Terminal, int]:
        min_value = math.inf
        min_terminal = None
        min_nr_reshuffles = math.inf
        for (term, reshuffles) in outcomes:
            value = reshuffles + self.value_function_approximator.value_approximate(self.n, current_batch_number + 1,
                                                                                    term, self.events)
            if value < min_value:
                min_value = value
                min_terminal = term
                min_nr_reshuffles = reshuffles
        if min_nr_reshuffles == ADP.NO_SOLUTION_COST:
            raise NoSolutionError("No solution for batch {}".format(self.events.batch(current_batch_number)))
        return min_terminal, min_nr_reshuffles

    ########################################################################################
    # Learning code
    ########################################################################################
    def determine_approximate_values(self):
        self.n = 1
        while self.n <= self.N:
            if self.single:
                self._iteration_single_pass(self.n)
            else:
                self._iteration_double_pass(self.n)

            self.value_function_approximator.on_iteration_done(self.n)

            if self.problem_instance > 0:
                print("Instance {}: {}/{}".format(self.problem_instance, self.n, self.N))

            if self.evaluate:
                # if every th iteration is the same as N, only a single evaluation at the end must be done
                if self.N == self.every_th_iteration:
                    if self.n == self.N:
                        self.evaluate_iteration(self.n)
                else:
                    if self.n % self.every_th_iteration == 1:
                        self.evaluate_iteration(self.n)

            self.n += 1

    def _iteration_single_pass(self, iteration: int):
        current_terminal = self.initial_terminal
        sample: RealizedEvents = self.events.sample()
        for t in range(sample.length()):
            try:
                outcome_terminal, value, _ = self.epsilon_greedy_policy(iteration, current_terminal, sample.batch(t), t)
                self.update_value_function(iteration, t, current_terminal, outcome_terminal, value)
                current_terminal = outcome_terminal
            except NoSolutionError:
                # noinspection PyTypeChecker
                self.update_value_function(iteration, t, current_terminal, None, ADP.NO_SOLUTION_COST)
                return

    def _iteration_double_pass(self, iteration: int):
        current_terminal = self.initial_terminal
        sample: RealizedEvents = self.events.sample()
        backtrace = []
        for t in range(sample.length()):
            try:
                outcome_terminal, _, nr_reshuffles = self.epsilon_greedy_policy(iteration, current_terminal,
                                                                                sample.batch(t), t)
                backtrace.append((current_terminal, outcome_terminal, nr_reshuffles))
                current_terminal = outcome_terminal
            except NoSolutionError:
                print("No Solution")
                # use double pass to propagate infinite cost.
                prev_value = ADP.NO_SOLUTION_COST
                for t_prime in reversed(range(len(backtrace))):
                    term, new_term, cost = backtrace[t_prime]
                    value = min(cost + self.discount_factor * prev_value, ADP.NO_SOLUTION_COST)
                    prev_value = value
                    self.update_value_function(iteration, t_prime, term, new_term, value)
                return

        prev_value = 0
        for t in reversed(range(len(backtrace))):
            term, new_term, cost = backtrace[t]
            value = cost + self.discount_factor * prev_value
            prev_value = value
            self.update_value_function(iteration, t, term, new_term, value)

    def solve_realization(self, iteration: int, terminal: Terminal, realized_batch: RealizedBatch, batch_number: int) \
            -> Tuple[Terminal, float, int]:
        """
        Solves the Bellman equation using the approximates of the previous iteration and returns the new state and the
        found value. In other words, solves:
        v^hat_t = min_{a_t \in \mathcal{A}_t} \{ C(S^n_t, a^n_t) + \lambda \bar{V}^{n-1}_t (S^M(S^n_t,  a^n_t)) \}
        :param iteration: current iteration being solved.
        :param terminal:
        :param realized_batch:
        :param batch_number:
        :return: The new state, the experience value of S_t and the number of reshuffles need in order to reach this
        layout. In other words, returns:  S^n_{t+1}, \hat{v}^n_t, #nr_reshuffles
        """
        min_value = math.inf
        min_terminal = None
        min_cost = math.inf
        for (outcome_terminal, cost) in terminal_unique_outcomes(terminal, realized_batch, self.corridor_size):
            # key = (batch_number+1, outcome_terminal.abstract())
            state_value = self.value_function_approximator.value_approximate(iteration, batch_number + 1,
                                                                             outcome_terminal, self.events)
            # state_value = self.approx_values.get(key, self.initial_approximation(batch_number+1, outcome_terminal))
            value = cost + self.discount_factor * state_value
            if value < min_value:
                min_value = value
                min_terminal = outcome_terminal
                min_cost = cost
        return min_terminal, min_value, min_cost

    def epsilon_greedy_policy(self, iteration: int, terminal: Terminal, realized_batch: RealizedBatch,
                              batch_number: int) \
            -> Tuple[Terminal, float, int]:
        # print("about to handle batch: {}: {}".format(batch_number, realized_batch))
        p = np.random.random()
        if p < self.epsilon:
            # explore
            if not self.use_optimized_outcomes:
                outcomes = terminal_unique_outcomes(terminal, realized_batch, self.corridor_size)
                outcome_terminal, nr_reshuffles = random.sample(outcomes, 1)[0]
                # key = (batch_number+1, outcome_terminal.abstract())
                state_value = self.value_function_approximator.value_approximate(iteration, batch_number + 1,
                                                                                 outcome_terminal, self.events)
                value = nr_reshuffles + self.discount_factor * state_value
            else:
                outcome_terminal, nr_reshuffles, value = terminal_optimized_outcome(terminal, realized_batch,
                                                                                    self.value_function_approximator,
                                                                                    iteration, batch_number,
                                                                                    self.events, self.corridor_size,
                                                                                    self.corridor_feature,
                                                                                    True)
        else:
            # exploit
            if not self.use_optimized_outcomes:
                outcome_terminal, value, nr_reshuffles = self.solve_realization(iteration, terminal, realized_batch,
                                                                                batch_number)
            else:
                outcome_terminal, nr_reshuffles, value = terminal_optimized_outcome(terminal, realized_batch,
                                                                                    self.value_function_approximator,
                                                                                    iteration, batch_number,
                                                                                    self.events, self.corridor_size,
                                                                                    self.corridor_feature, False)

        return outcome_terminal, value, nr_reshuffles

    def update_value_function(self,
                              n: int,
                              t: int,
                              previous_terminal: Terminal,
                              new_terminal: Terminal,
                              observed_value: float):
        self.value_function_approximator.on_sample_realization(n, t, previous_terminal, new_terminal, observed_value,
                                                               self.events)

    def evaluate_iteration(self, n):
        self.events.sample_count_evaluating = 0
        sample_results = []
        for sample_iteration in range(self.evaluation_samples):
            try:
                # noinspection PyUnresolvedReferences
                sample = self.events.sample_evaluating()
                new_terminal = self.initial_terminal
                total_reshuffles = 0
                for batch_number in range(self.events.length()):
                    new_terminal, reshuffles = self.handle_realized_batch(new_terminal,
                                                                          sample.batch(batch_number),
                                                                          batch_number)
                    total_reshuffles += reshuffles

                sample_results.append(total_reshuffles)
            except NoSolutionError:
                sample_results.append(ADP.NO_SOLUTION_COST)

        m, std = mean(sample_results), stdev(sample_results)
        initial_state_value = self.value_function_approximator.value_approximate(n, 0, self.initial_terminal,
                                                                                 self.events)

        self.evaluation_results[n] = (m, std, initial_state_value)
