import unittest
from typing import List

from main.model.adp.valuefunctions.basisfunction import BasisFunction
from main.model.adp.valuefunctions.features.compositeMeasure import MM_rule
from main.model.batch import RealizedBatch
from main.model.dataclass import Container
from main.model.dataclass.block import Block
from main.model.dataclass.outcomes import terminal_unique_outcomes, valid_store_location
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal
from main.model.events.events import Events
from main.model.policies.adp import ADP


class TestExactPolicy(unittest.TestCase):
    events = Events.create([(1, 2), (), (3,), (2, 3)])
    init_terminal = Terminal.empty_single_stack_block(2, 4)

    t = Terminal((
            Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
        ), 2).store_container((0,0), (10,10,-1)).store_container((0,0), (11,11,-1)).store_container((0,4), (12,12,-1))

    t2 = Terminal((
            Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
            Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
            Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True)
        ), 4)

    # def test_weights_basis(self):
    #     events = Events.create([(1,2), (1,), (), (), (), (2,)])
    #     print(events)
    #
    #     feature_list = [average_stack_height, blocking_lower_bound, empty_stacks, topmost_unordered, unordered_stacks]
    #     value_function_approx = BasisFunction(feature_list, 1.0, delta=0.5)
    #     adp = ADP(events, self.init_terminal, True, 0.05, value_function_approx, 5, 1, False)
    #     print("done")

    # def test_basis(self):
    #     feature_list = [lambda x: 3, lambda x: 7]
    #     basis = BasisFunction(feature_list, 1.0, 0.1)
    #
    #     for n in range(1, 11):
    #         for t in reversed(range(4)):
    #             basis.on_sample_realization(n, t, None, None, 1)
    #         basis.on_iteration_done(n)
    #     print(basis.value_approximate(10, 0, None))

    # def test_no_sol(self):
    #     events = Events.create([(1,), (1,), (2,3), (), (), (2,)])
    #     print(events)
    #
    #     feature_list = [average_stack_height, blocking_lower_bound, empty_stacks, topmost_unordered, unordered_stacks]
    #     value_function_approx = BasisFunction(feature_list, 1.0, delta=0.5)
    #     adp = ADP(events, self.t, False, 0.05, value_function_approx, 5, 1, False)
    #     print("done")

    def test_hard_outcome_instance(self):
        """
-37_?(22)∣22_?(28)∣21_?(18)
-21_?(19)
-21_?(10)
-19_?(4)
-23_?(7)∣22_?(20)
**
-22_?(12)∣38_?(15)∣35_?(0)∣24_?(23)
-19_?(16)
-
-
-19_?(17)∣23_?(27)∣31_?(25)∣51_?(6)
        """
        t = Terminal((
            Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
            Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True)
        ), 4)
        t = t.store_container((0,0), (22,37,-1)).store_container((0,0), (28,22,-1)).store_container((0,0), (21,37,-1))
        t = t.store_container((0,1), (19,21,-1))
        t = t.store_container((0,2), (10,21,-1))
        t = t.store_container((0,3), (4,19,-1))
        t = t.store_container((0,4), (7,23,-1)).store_container((0,4), (20,22,-1))

        t = t.store_container((1,0), (12,22,-1)).store_container((1,0),(15,38,-1)).store_container((1,0),(0,38,-1)).store_container((1,0),(23,24,-1))
        t = t.store_container((1,1), (16,19,-1))
        t = t.store_container((1,4),(17,19,-1)).store_container((1,4),(27,23,-1)).store_container((1,4),(25,31,-1)).store_container((1,4),(6,51,-1))

        # outcomes = terminal_unique_outcomes(t, RealizedBatch(False, ( (17, 19, -1), (4, 19, -1), (16, 19, -1))))
        total_set = set()
        outcomes1 = terminal_unique_outcomes(t, RealizedBatch(False, ((17, 19, -1),)))
        for term, reshuffle in outcomes1:
            outcomes2 = terminal_unique_outcomes(term, RealizedBatch(False, ((4, 19, -1),)))
            total_set.update(outcomes2)
            print(len(outcomes2))

        # outcomes = terminal_unique_outcomes(t, RealizedBatch(False, ( (17, 19, -1), (4, 19, -1))))




    def test_failing_instance_MMRule(self):
        t = self.t2.store_container((0,0), (7,12,-1))
        t = t.store_container((0,1), (2,14,-1)).store_container((0,1), (10,18,-1))
        t = t.store_container((0,2), (18,10,-1))
        t = t.store_container((0,3), (5,16,-1)).store_container((0,3), (19,11,-1))
        t = t.store_container((0,4), (23,11,-1))

        t = t.store_container((1,2), (21,20,-1))
        t = t.store_container((1,3), (8,13,-1))

        t = t.store_container((2,2), (9,10,-1)).store_container((2,2), (0,10,-1))


    def test_stairs_valid_locations(self):
        c: List[Container] = [(i, i, -1) for i in range(20)]
        t = self.t2.store_container((0,0), c[0])
        t = t.store_container((0,1), c[1]).store_container((0,1), c[2])
        t = t.store_container((0,2), c[3])
        t = t.store_container((0,3), c[1]).store_container((0,3), c[2])
        t = t.store_container((0,4), c[4])


        self.assertTrue(valid_store_location(t, (0,0), None))
        self.assertTrue(valid_store_location(t, (0,1), None))
        self.assertTrue(valid_store_location(t, (0,3), None))
        self.assertTrue(valid_store_location(t, (0,4), None))

        self.assertFalse(valid_store_location(t, (0,2), None))

        self.assertFalse(valid_store_location(t, (0,0), (0,2,0)))
        self.assertFalse(valid_store_location(t, (0,1), (0,2,0)))
        self.assertFalse(valid_store_location(t, (0,2), (0,2,0)))
        self.assertFalse(valid_store_location(t, (0,3), (0,2,0)))
        self.assertFalse(valid_store_location(t, (0,4), (0,2,0)))



