import unittest

from main.model.batch.realizedBatch import RealizedBatch
from main.model.dataclass.block import Block
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal
from main.model.events.evaluatableEvents import EvaluatableEvents
from main.model.events.events import Events
from main.model.policies.pbfs import PBFS
from main.model.policies.policy import Policy


class TestExactPolicy(unittest.TestCase):
    events = Events.create([(1, 2), (), (3,), (2, 3)])
    init_terminal = Terminal.empty_single_stack_block(2, 4)
    pbfs = PBFS(events, init_terminal)

    c1 = (1,2,-1)
    c2 = (2,1,-1)
    c3 = (3,1,-1)

    def PBFS1(self, t, t_done):
        term, reshuffles = self.pbfs.handle_realized_batch(t, RealizedBatch(False, (self.c2, self.c3)), 3)

        self.assertEqual(term, t_done)
        self.assertEqual(reshuffles, 1)

        term, reshuffles = self.pbfs.handle_realized_batch(t, RealizedBatch(False, (self.c3, self.c2)), 3)

        self.assertEqual(term, t_done)
        self.assertEqual(reshuffles, 0)

    def test_PBFS1(self):
        t = Terminal(
            (
                Block(
                    (
                        Stack((self.c1,)),
                    ), False
                ),
                Block(
                    (
                        Stack((self.c2, self.c3)),
                    ), False
                ),
            ),
            4
        )
        t_done = Terminal(
            (
                Block(
                    (
                        Stack((self.c1,)),
                    ), False
                ),
                Block(
                    (
                        Stack(()),
                    ), False
                ),
            ),
            4
        )
        self.PBFS1(t, t_done)

    def test_PBFS2(self):
        t = Terminal(
            (
                Block((Stack((self.c2, self.c3)),), False),
                Block((Stack((self.c1,),),), False)
            ),
            4
        )
        t_done = Terminal(
            (
                Block((Stack((),),), False),
                Block((Stack((self.c1,),),), False)
            ),
            4
        )
        self.PBFS1(t, t_done)

    def test_PBFS3(self):
        t = Terminal.empty_single_stack_block(2, 4)

        term, reshuffles = self.pbfs.handle_realized_batch(t, RealizedBatch(True, (self.c1, self.c2)), 0)

        self.assertEqual(reshuffles, 0)

    @staticmethod
    def evaluate_pbfs(events, init_terminal, pbfs):
        total_reshuffles = 0
        for i in range(10):
            sample = events.sample()
            new_terminal = init_terminal
            for batch_number in range(events.length()):
                # print("-" * 40)
                # print(new_terminal.reveal_order(sample.batch(batch_number).containers))
                new_terminal, reshuffles = pbfs.handle_realized_batch(new_terminal, sample.batch(batch_number),
                                                                           batch_number)
                total_reshuffles += reshuffles

        return total_reshuffles/100

    def test_realization(self):
        total_reshuffles = self.evaluate_pbfs(self.events, self.init_terminal, self.pbfs)

        self.assertEqual(total_reshuffles, 0)

    def test_case(self):
        events = EvaluatableEvents.create_from_ids([(1, 2), (1,), (3,), ()])
        t = Terminal.empty_single_stack_block(2, 4)
        pbfs = PBFS(events, t)
        total_reshuffles = self.evaluate_pbfs(events, t, pbfs)
        self.assertEqual(total_reshuffles, 0)

    def test_case2(self):
        events = Events.create([(1,2,3), (), (), (1,2,3)])
        t = Terminal.empty_single_stack_block(2, 3)
        pbfs = PBFS(events, t)
        # print(self.evaluate_pbfs(events, t, pbfs))
        self.assertNotEqual(self.evaluate_pbfs(events, t, pbfs), 0)



