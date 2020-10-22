import unittest
from typing import List

from main.model.batch import RealizedBatch
from main.model.dataclass import Container
from main.model.dataclass.block import Block
from main.model.dataclass.outcomes import terminal_unique_outcomes, valid_store_location
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal


class TestBayOutcomes(unittest.TestCase):
    c: List[Container] = [(i, i, -1) for i in range(20)]
    t = Terminal((
        Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
        Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
        Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True)
    ), 4)

    def test_bay_outcomes(self):
        t = Terminal((
            Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
            Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True)
        ), 3)
        t = t.store_container((0,0), self.c[10]).store_container((0,0), self.c[11]).store_container((0,0), self.c[12])
        t = t.store_container((0,4), self.c[0]).store_container((0,4), self.c[14]).store_container((0,4), self.c[15])

        t = t.store_container((1,0), self.c[16]).store_container((1,0), self.c[17]).store_container((1,0), self.c[19])
        t = t.store_container((1, 1), self.c[1])
        t = t.store_container((1,4), self.c[18])



        outcomes = terminal_unique_outcomes(t, RealizedBatch(False, (self.c[0],)))
        # for term, reshuffles in outcomes:
        #     print(term)
        self.assertEqual(len(outcomes), 1)

        outcomes = terminal_unique_outcomes(t, RealizedBatch(False, (self.c[0], self.c[1])))
        # for term, reshuffles in outcomes:
        #     print(term)
        self.assertEqual(len(outcomes), 4)


    def test_valid_location(self):
        t = Terminal((
            Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
            Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True)
        ), 3)

        t = t.store_container((0,2), self.c[0]).store_container((0,2), self.c[1]).store_container((0,2), self.c[2])
        self.assertFalse(valid_store_location(t, (0,1), (0,2,0)))
        self.assertFalse(valid_store_location(t, (0,3), (0,2,0)))

    def test_simple_outcomes(self):
        t = self.t.store_container((0,2), self.c[0])\
            .store_container((0,2), self.c[3])\
            .store_container((0,2), self.c[2])\
            .store_container((0,2), self.c[1])

        outcomes = terminal_unique_outcomes(t, RealizedBatch(False, (self.c[0],)))

        self.assertEqual(len(outcomes), 12)

        outcomes = terminal_unique_outcomes(t, RealizedBatch(False, (self.c[0], self.c[1], self.c[2])))
        self.assertEqual(len(outcomes), 3)
        outcomes = terminal_unique_outcomes(t, RealizedBatch(False, (self.c[0], self.c[1], self.c[2], self.c[3])))
        self.assertEqual(len(outcomes), 1)


    def test_valid_3(self):
        t = self.t.store_container((0,0), self.c[0]).store_container((0,2), self.c[1]).store_container((0,2), self.c[2])
        self.assertFalse(valid_store_location(t, (0,1), None))

        t = t.store_container((0,1), self.c[2]).store_container((0,1), self.c[3])
        self.assertTrue(valid_store_location(t, (0, 1), None))

