import unittest

from main.model.dataclass.block import Block
from main.model.dataclass.outcomes import corridor
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal


class TestCorridor(unittest.TestCase):
    terminal = Terminal.empty_bay(10, 4)
    designated_terminal = Terminal((
        Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True, 0),
        Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True, 0),
        Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True, 0),
        Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True, 1),
        Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True, 1),
        Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True, 1),
        Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True, 1),
        Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True, 1),
        Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True, 0),
        Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True, 0),
    ), 4)

    def test_zero_corridor(self):
        self.assertListEqual([5], corridor(self.terminal, (5, 0, 0), 0, 0))

    def test_single_corridor_1(self):
        self.assertCountEqual([4,5,6], corridor(self.terminal, (5, 0, 0), 1, 0))

    def test_single_corridor_2(self):
        self.assertCountEqual([8,9,0], corridor(self.terminal, (9, 0, 0), 1, 0))

    def test_double_corridor_1(self):
        self.assertCountEqual([6,7,8,9,0], corridor(self.terminal, (8, 0, 0), 2, 0))

    def test_double_corridor_2(self):
        self.assertCountEqual([9,0,1,2,3], corridor(self.terminal, (1, 0, 0), 2, 0))

    def test_designated_with_label_single(self):
        self.assertCountEqual([7,3,4], corridor(self.designated_terminal, (3, 0, 0), 1, 1))

    def test_designated_with_label_double(self):
        self.assertCountEqual([6,7,3,4,5], corridor(self.designated_terminal, (3, 0, 0), 2, 1))

    def test_designated_without_label_single(self):
        self.assertCountEqual([2,3,4], corridor(self.designated_terminal, (3, 0, 0), 1, 0))

    def test_designated_without_label_double(self):
        self.assertCountEqual([0,1,2,3,4], corridor(self.designated_terminal, (2, 0, 0), 2, 0))

    def test_designated_without_label_triple(self):
        self.assertCountEqual([9,0,1,2,3,4,5], corridor(self.designated_terminal, (2, 0, 0), 3, 0))

    def test_with_no_corridor(self):
        self.assertCountEqual(list(range(10)), corridor(self.designated_terminal, (2, 0, 0), -1, 0))