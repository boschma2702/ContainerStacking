import unittest
from typing import List

from main.model.batch.realizedBatch import RealizedBatch
from main.model.dataclass import Container
from main.model.dataclass.block import Block
from main.model.dataclass.outcomes import store_locations, _reachable, _unique_outbound_outcomes
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal
from main.model.events.evaluatableEvents import EvaluatableEvents
from main.model.events.events import Events
from main.model.noSolutionError import NoSolutionError
from main.model.policies.pbfs import PBFS
from main.model.policies.policy import Policy
from test.policy.testPBFS import TestExactPolicy


class TestExactPolicyBay(unittest.TestCase):
    t = Terminal((
        Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
    ), 4)
    c: List[Container] = [(i, i, -1) for i in range(10)]


    def test_store_locations(self):
        self.assertEqual(len(store_locations(self.t, self.c[0], None)), 1)

        # self.t.store_container((), self.c[0])

    def test_block_reachable1(self):
        b = Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), False)
        for i in range(len(b.stacks)):
            self.assertTrue(_reachable(b, i))

        b2 = b.store_container(0, self.c[0])
        self.assertTrue(_reachable(b2, 0))

        self.assertFalse(_reachable(b2, 1))
        self.assertFalse(_reachable(b2, 2))
        self.assertFalse(_reachable(b2, 3))
        self.assertFalse(_reachable(b2, 4))


    def test_block_reachable(self):
        b = Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True)
        for i in range(len(b.stacks)):
            self.assertTrue(_reachable(b, i))

        b2 = b.store_container(0, self.c[0])
        for i in range(len(b2.stacks)):
            self.assertTrue(_reachable(b2, i))

        b2 = b2.store_container(4, self.c[1])
        self.assertTrue(_reachable(b2, 0))
        self.assertTrue(_reachable(b2, 4))

        self.assertFalse(_reachable(b2, 1))
        self.assertFalse(_reachable(b2, 2))
        self.assertFalse(_reachable(b2, 3))


    def test_block_blocking1(self):
        t = self.t.store_container((0,0), self.c[0])
        outcomes = _unique_outbound_outcomes(t, RealizedBatch(False, (self.c[0],)))

        self.assertEqual(len(outcomes), 1)
        self.assertEqual(outcomes.__iter__().__next__()[1], 0)

