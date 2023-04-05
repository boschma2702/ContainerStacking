import unittest
from typing import List

from main.model.batch import RealizedBatch
from main.model.dataclass import Container
from main.model.dataclass.block import Block
from main.model.dataclass.outcomes import valid_store_location, store_locations, terminal_unique_outcomes
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal
from main.model.events.evaluatableEvents import EvaluatableEvents


class TestOutcomes(unittest.TestCase):
    c: List[Container] = [(i, i, -1) for i in range(20)]
    t = Terminal(
        (
            Block(
                (
                    Stack(((1, 1, -1), (2, 1, -1), (3, 1, -1), (4, 1, -1),)),
                    Stack(((1, 1, -1), (2, 1, -1), (3, 1, -1))),
                ), True
            ),
            Block(
                (
                    Stack(()),
                ), False
            )
        ), 4
    )
    t2 = Terminal(
        (
            Block(
                (
                    Stack((c[0],)),
                    Stack((c[1], c[2])),
                    Stack((c[3], c[4], c[5])),
                    Stack((c[6],)),
                    Stack(()),
                ), False
            ),
        ), 4
    )
    t3 = Terminal((Block(t2.blocks[0].stacks, True),), 4)
    t_block = Terminal.empty_bay(1, 4)

    def test_valid_store_height(self):
        self.assertEqual(valid_store_location(self.t, (0, 0), None), False)
        self.assertEqual(valid_store_location(self.t, (0, 1), None), True)
        self.assertEqual(valid_store_location(self.t, (1, 0), None), True)

    def test_valid_store_no_new_reshuffles_in_block(self):
        self.assertEqual(valid_store_location(self.t2, (0,2), None), True)
        self.assertEqual(valid_store_location(self.t2, (0,1), None), True)
        self.assertEqual(valid_store_location(self.t2, (0,0), None), True)
        self.assertEqual(valid_store_location(self.t2, (0,3), None), False)
        self.assertEqual(valid_store_location(self.t2, (0,4), None), False)

        self.assertEqual(valid_store_location(self.t3, (0,2), None), True)
        self.assertEqual(valid_store_location(self.t3, (0,1), None), True)
        self.assertEqual(valid_store_location(self.t3, (0,0), None), True)
        self.assertEqual(valid_store_location(self.t3, (0,3), None), True)
        self.assertEqual(valid_store_location(self.t3, (0,4), None), True)

    def test_valid_store_excluded_location(self):
        self.assertEqual(valid_store_location(self.t, (0, 1), (0, 1, 0)), False)
        self.assertEqual(valid_store_location(self.t, (0, 1), (0, 1, 1)), False)
        self.assertEqual(valid_store_location(self.t, (0, 1), (0, 1, 2)), False)
        self.assertEqual(valid_store_location(self.t, (0, 1), (0, 1, 3)), False)
        self.assertEqual(valid_store_location(self.t, (0, 1), (0, 1, 4)), False)

        self.assertEqual(valid_store_location(self.t, (0, 0), (0, 1, 0)), False)
        self.assertEqual(valid_store_location(self.t, (0, 0), (0, 1, 1)), False)
        self.assertEqual(valid_store_location(self.t, (0, 0), (0, 1, 2)), False)
        self.assertEqual(valid_store_location(self.t, (0, 0), (0, 1, 3)), False)
        self.assertEqual(valid_store_location(self.t, (0, 0), (0, 1, 4)), False)

        self.assertEqual(valid_store_location(self.t, (0, 1), (1, 0, 0)), True)
        self.assertEqual(valid_store_location(self.t, (0, 1), (1, 0, 1)), True)
        self.assertEqual(valid_store_location(self.t, (0, 1), (1, 0, 2)), True)
        self.assertEqual(valid_store_location(self.t, (0, 1), (1, 0, 3)), True)
        self.assertEqual(valid_store_location(self.t, (0, 1), (1, 0, 4)), True)

    def test_store_locations(self):
        self.assertEqual(len(store_locations(self.t, (5,5,-1), None)), 2)
        self.assertEqual(len(store_locations(self.t2, (5,5,-1), None)), 3)
        self.assertEqual(len(store_locations(self.t3, (5,5,-1), None)), 5)

        self.assertEqual(len(store_locations(self.t, (5, 5, -1), (0,0,0))), 1)
        self.assertEqual(len(store_locations(self.t, (5, 5, -1), (0,0,1))), 1)

        self.assertEqual(len(store_locations(self.t, (5, 5, -1), (0,1,0))), 1)

        self.assertEqual(len(store_locations(self.t2, (5, 5, -1), (0,0,0))), 2)
        self.assertEqual(len(store_locations(self.t2, (5, 5, -1), (0,0,1))), 0)

        self.assertEqual(len(store_locations(self.t3, (5, 5, -1), (0, 0, 0))), 2)

        t = self.t3.store_container((0,0), self.c[6])
        self.assertEqual(len(store_locations(t, (5, 5, -1), None)), 4)

        t = t.store_container((0,0), self.c[7])
        self.assertEqual(len(store_locations(t, (5, 5, -1), None)), 4)

        t = t.store_container((0, 0), self.c[8])
        self.assertEqual(len(store_locations(t, (5, 5, -1), None)), 3)

    def test_retrieve_outcomes(self):
        # events = EvaluatableEvents.create_from_ids([(1, 2), (), (3,), (2, 3)])
        t = Terminal.empty_single_stack_block(2, 4)
        t = t.store_container((0,0), (2,1,-1))\
            .store_container((0,0), (1,2,-1))\
            .store_container((0,0), (3,1,-1))

        outcomes = terminal_unique_outcomes(t, RealizedBatch(False, ((2, 1, -1), (3, 1, -1))))
        self.assertEqual(len(outcomes), 1)

        term, reshuffles = list(outcomes)[0]
        self.assertEqual(term, Terminal.empty_single_stack_block(2, 4).store_container((0,0), (1,2,-1)))
        self.assertEqual(reshuffles, 3)


    def test_stacks_position_bay(self):
        t = Terminal((
            Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
            Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), False)
        ), 3)
        t = t.store_container((0,2), self.c[0])

        self.assertTrue(valid_store_location(t, (0,2), None))

    def test_empty_bay(self):
        self.assertFalse(valid_store_location(self.t_block, (0,0), None))
        self.assertFalse(valid_store_location(self.t_block, (0,1), None))
        self.assertTrue(valid_store_location(self.t_block, (0,2), None))
        self.assertFalse(valid_store_location(self.t_block, (0,3), None))
        self.assertFalse(valid_store_location(self.t_block, (0,4), None))






