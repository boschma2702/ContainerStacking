import unittest
from typing import List

from main.model.batch.realizedBatch import RealizedBatch
from main.model.dataclass import Container
from main.model.dataclass.block import Block
from main.model.dataclass.outcomes import _unique_outbound_outcomes
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal
from main.model.noSolutionError import NoSolutionError


class TestBayBlocking(unittest.TestCase):
    t = Terminal((
        Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
    ), 4)
    c: List[Container] = [(i, i, -1) for i in range(10)]

    def test_block_blocking1(self):
        t = self.t.store_container((0, 0), self.c[0])
        outcomes = _unique_outbound_outcomes(t, RealizedBatch(False, (self.c[0],)))

        self.assertEqual(len(outcomes), 1)
        self.assertEqual(outcomes.__iter__().__next__()[1], 0)


    def test_block_blocking2(self):
        t = self.t.store_container((0, 1), self.c[0]).store_container((0, 0), self.c[1]).store_container((0, 2), self.c[2])
        outcomes = _unique_outbound_outcomes(t, RealizedBatch(False, (self.c[0],)))

        self.assertEqual(len(outcomes), 3)
        for term, reshuffles in outcomes:
            self.assertEqual(reshuffles, 1)



    def test_block_not_solvable(self):
        t = self.t.store_container((0, 2), self.c[0])\
            .store_container((0, 0), self.c[1])\
            .store_container((0, 0), self.c[2])\
            .store_container((0, 4), self.c[4])\
            .store_container((0, 4), self.c[5])\
            .store_container((0, 4), self.c[6])

        self.assertRaises(NoSolutionError, _unique_outbound_outcomes, t, RealizedBatch(False, (self.c[0],)))
