from __future__ import annotations

from statistics import stdev, mean
from typing import Tuple

from main.model.batch.realizedBatch import RealizedBatch
from main.model.dataclass.terminal import Terminal
from main.model.events.evaluatableEvents import EvaluatableEvents
from main.model.events.events import Events


class Policy:

    nr_samples = 1000

    def __init__(self, events: Events, initial_terminal: Terminal):
        self.events = events
        self.initial_terminal = initial_terminal

    def handle_realized_batch(self, terminal: Terminal, realized_batch: RealizedBatch, batch_number: int) \
            -> Tuple[Terminal, int]:
        if realized_batch.inbound:
            return self.handle_realized_inbound_batch(terminal, realized_batch, batch_number)
        else:
            t = terminal.reveal_order(realized_batch.containers)
            return self.handle_realized_outbound_batch(t, realized_batch, batch_number)

    def handle_realized_inbound_batch(self, terminal: Terminal, realized_batch: RealizedBatch, batch_number: int)\
            -> Tuple[Terminal, int]:
        raise NotImplementedError('Should be implemented by policy')

    def handle_realized_outbound_batch(self, terminal: Terminal, realized_batch: RealizedBatch, batch_number: int)\
            -> Tuple[Terminal, int]:
        raise NotImplementedError('Should be implemented by policy')

    @staticmethod
    def evaluate(policy: Policy, initial_terminal: Terminal, events: EvaluatableEvents, nr_samples=nr_samples, reset=True):
        if reset:
            events.reset()

        sample_results = []
        for sample_iteration in range(nr_samples):
            sample = events.sample_evaluating()
            new_terminal = initial_terminal
            total_reshuffles = 0
            for batch_number in range(events.length()):
                new_terminal, reshuffles = policy.handle_realized_batch(new_terminal, sample.batch(batch_number),
                                                                        batch_number)
                total_reshuffles += reshuffles
            sample_results.append(total_reshuffles)
        return mean(sample_results), stdev(sample_results)
