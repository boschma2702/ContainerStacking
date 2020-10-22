import unittest
from typing import List

from main.model.batch import RealizedBatch
from main.model.dataclass import Container
from main.model.dataclass.block import Block
from main.model.dataclass.outcomes import _unique_inbound_outcomes, store_locations
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal


class TestUniqueInboundOutcomes(unittest.TestCase):
    c: List[Container] = [(i, i, -1) for i in range(10)]

    def test_equality(self):
        t = Terminal.empty_single_stack_block(100, 4)
        realized_batch = RealizedBatch(True, (self.c[0],))
        self.assertEqual(len(_unique_inbound_outcomes(t, realized_batch)), 1)
        self.assertEqual(len(_unique_inbound_outcomes(t, RealizedBatch(True, (self.c[0], self.c[1])))), 2)

    def test_store_location(self):
        t = Terminal.empty_single_stack_block(100, 4)
        self.assertEqual(len(store_locations(t, self.c[0], None)), 1)

        b1 = Block.empty_single_stack()
        s = set()
        s.add(Block.empty_single_stack().store_container(0, self.c[1]))
        s.add(Block.empty_single_stack().store_container(0, self.c[1]))
        s.add(Block.empty_single_stack().store_container(0, (2,1,-1)))
        self.assertEqual(len(s), 1)

        tup = (b1.store_container(0, self.c[1]), b1.store_container(0, self.c[1]), b1.store_container(0, (2,1,-1)))
        self.assertEqual(len(set(tup)), 1)
