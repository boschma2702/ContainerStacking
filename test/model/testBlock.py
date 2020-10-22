import unittest
from typing import List

from main.model.dataclass import Container
from main.model.dataclass.block import Block
from main.model.dataclass.stack import Stack


class TestStackBlock(unittest.TestCase):

    def test_equality(self):
        b1 = Block.empty_single_stack()
        b2 = Block.empty_single_stack()

        self.assertEqual(b1, b2)
        self.assertNotEqual(b1, b2.store_container(0, (1, 1, -1)))
        self.assertNotEqual(b1.store_container(0, (2, 2, -1)), b2.store_container(0, (1, 1, -1)))
        self.assertEqual(b1.store_container(0, (2, 1, -1)), b2.store_container(0, (1, 1, -1)))
        self.assertTrue(b1.store_container(0, (2, 1, -1)) <= b2.store_container(0, (1, 1, -1)))

    def test_order(self):
        b1 = Block((Stack(((1,1,-1),)), Stack(())), False)
        b2 = Block((Stack(((1,1,-1),)),), False)
        self.assertTrue(b2 < b1)

    def test_store(self):
        b1 = Block(
            (
                Stack(((1, 1, -1),)),
            ), False
        )
        b2 = Block.empty_single_stack()

        self.assertNotEqual(b1, b2)
        self.assertEqual(b1, b2.store_container(0, (1, 1, -1)))
        self.assertEqual(b1.store_container(0, (2, 2, -1)),
                         b2.store_container(0, (1, 1, -1)).store_container(0, (2, 2, -1)))

    def test_retrieve(self):
        b1 = Block(
            (
                Stack(((1, 1, -1),(2, 2, -1),)),
            ), False
        )
        b2 = Block(
            (
                Stack(((1, 1, -1),)),
            ), False
        )
        block, container = b1.retrieve_container(0)
        block2, container2 = block.retrieve_container(0)

        self.assertEqual(container, (2,2,-1))
        self.assertEqual(block, b2)
        self.assertEqual(container2, (1,1,-1))
        self.assertEqual(block2, Block.empty_single_stack())

    def test_abstract_block1(self):
        b1 = Block(
            (
                Stack((), ),
            )
            , True
        )
        b2 = Block(
            (
                Stack((), ),
            )
            , False
        )
        b3 = Block(
            (
                Stack((), ),
                Stack((), )
            )
            , True
        )
        b4 = Block(
            (
                Stack((), ),
                Stack(((1, 1, -1), ), )
            )
            , True
        )

        self.assertNotEqual(b1, b2)
        self.assertNotEqual(b1, b3)
        self.assertNotEqual(b1, b4)
        self.assertNotEqual(b3, b4)

        self.assertNotEqual(b1.abstract(), b2.abstract())

        self.assertEqual(b3.store_container(1, (2, 1, -1)), b4)
        self.assertEqual(b3.store_container(0, (2, 1, -1)).abstract(), b4)
        self.assertEqual(b3.store_container(1, (2, 1, -1)).abstract(), b4.abstract())
        self.assertNotEqual(b3.store_container(0, (2, 1, -1)), b4)

    def test_abstract_block2(self):
        b1 = Block(
            (
                Stack((), ),
                Stack((), )
            )
            , True
        )
        b2 = Block(
            (
                Stack((), ),
                Stack((), )
            )
            , False
        )

        self.assertNotEqual(b1, b2)
        self.assertNotEqual(b1.store_container(0, (1,1,-1)), b1.store_container(1, (1,1,-1)))
        self.assertEqual(b1.store_container(0, (1,1,-1)).abstract(), b1.store_container(1, (1,1,-1)))
        self.assertEqual(b1.store_container(0, (1,1,-1)).abstract(), b1.store_container(1, (1,1,-1)).abstract())

        self.assertNotEqual(b2.store_container(0, (1, 1, -1)), b2.store_container(1, (1, 1, -1)))
        self.assertNotEqual(b2.store_container(0, (1, 1, -1)).abstract(), b2.store_container(1, (1, 1, -1)))
        self.assertNotEqual(b2.store_container(0, (1, 1, -1)).abstract(), b2.store_container(1, (1, 1, -1)).abstract())

    def test_reveal(self):
        b1 = Block(
            (
                Stack(((2,2,-1), (3,2,-1)), ),
                Stack(((1, 1, -1), ), )
            )
            , False
        )
        b2 = Block(
            (
                Stack(((2, 2, 2), (3, 2, 1)), ),
                Stack(((1, 1, -1),), )
            )
            , False
        )
        self.assertEqual(b1.reveal_order({3:1, 2:2}), b2)

    def test_blocking_reachstacker1(self):
        c: List[Container] = [(i, i, -1) for i in range(5)]
        b1 = Block(
            (
                Stack((c[1], c[2]), ),
                Stack((c[3],), )
            )
            , False
        )
        b2 = Block(b1.stacks, True)
        self.assertEqual(b1.blocking_containers((0, 0)), [c[2]])
        self.assertEqual(b1.blocking_containers((0, 1)), [])
        self.assertEqual(b1.blocking_containers((1, 0)), [c[2], c[1]])
        self.assertNotEqual(b1.blocking_containers((1, 0)), [c[1], c[2]])

        self.assertEqual(b2.blocking_containers((0, 0)), [c[2]])
        self.assertEqual(b2.blocking_containers((0, 1)), [])
        self.assertEqual(b2.blocking_containers((1, 0)), [])

    def test_blocking_reachstacker2(self):
        c: List[Container] = [(i, i, -1) for i in range(10)]
        b1 = Block(
            (
                Stack((c[1], c[2]), ),
                Stack((c[3], c[4], c[5]), ),
                Stack((c[6], ), ),
            )
            , False
        )
        b2 = Block(b1.stacks, True)

        self.assertEqual(b1.blocking_containers((1, 2)), [])
        self.assertEqual(b1.blocking_containers((1, 1)), [c[2], c[5]])
        self.assertEqual(b1.blocking_containers((1, 0)), [c[2], c[1], c[5], c[4]])

        self.assertEqual(b2.blocking_containers((1, 2)), [])
        self.assertEqual(b2.blocking_containers((1, 1)), [c[5]])
        self.assertEqual(b2.blocking_containers((1, 0)), [c[6], c[5], c[4]])

        self.assertEqual(b2.blocking_containers((0, 0)), [c[2]])

    def test_blocking_reachstacker_single_stack(self):
        b = Block((Stack(()),), False)
        self.assertEqual(b.blocking_containers((0, 0)), [])
        self.assertEqual(b.blocking_containers((0, 1)), [])
        c1 = (1,1,-1)
        c2 = (2,2,-1)
        b = b.store_container(0, c1)
        self.assertEqual(b.blocking_containers((0, 0)), [])
        b = b.store_container(0, c2)
        self.assertEqual(b.blocking_containers((0, 0)), [c2])
        self.assertEqual(b.blocking_containers((0, 1)), [])
