import unittest

from main.model.dataclass.block import Block
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal


class TestStruct(unittest.TestCase):
    t1 = Terminal(
        (
            Block(
                (
                    Stack(((1, 1, -1),)),
                ), False
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
                    Stack(((1, 1, -1),)),
                ), False
            ),
            Block(
                (
                    Stack(((2, 2, -1),)),
                ), False
            )
        ), 4
    )

    t3 = Terminal(
        (
            Block(
                (
                    Stack(((3, 3, 1),)),
                    Stack(())
                ), True
            ),
        ), 4
    )

    t4 = Terminal(
        (
            Block(
                (
                    Stack(()),
                    Stack(())
                ), True
            ),
        ), 4
    )

    def test_store(self):
        self.assertEqual(self.t1.store_container((1, 0), (2, 2, -1)), self.t2)
        self.assertEqual(self.t4.store_container((0, 0), (3, 3, 1)), self.t3)

    def test_retrieve(self):
        term, container = self.t2.retrieve_container((1, 0))
        self.assertEqual(container, (2, 2, -1))
        self.assertEqual(term, self.t1)

        term, container = self.t3.retrieve_container((0, 0))
        self.assertEqual(container, (3, 3, 1))
        self.assertEqual(term, self.t4)

    def test_store_retrieve(self):
        term, container = self.t1.retrieve_container((0, 0))
        term2 = term.store_container((0, 0), container)
        self.assertEqual(term2, self.t1)

        term = self.t3.store_container((0, 0), (1, 1, 1))
        term2, container = term.retrieve_container((0, 0))
        self.assertEqual(container, (1, 1, 1))
        self.assertEqual(term2, self.t3)
        pass

    def test_reshuffle(self):
        term, container = self.t1.retrieve_container((0, 0))
        term = term.store_container((1, 0), container)
        term = term.reshuffle_container((1, 0), (0, 0))
        self.assertEqual(term, self.t1)

        term = self.t4.store_container((0, 1), (3, 3, 1))
        term = term.reshuffle_container((0, 1), (0, 0))
        self.assertEqual(term, self.t3)
        pass

    def test_equality(self):
        term = self.t4.store_container((0, 1), (5, 3, 1))
        self.assertNotEqual(self.t4, self.t3)
        self.assertNotEqual(term, self.t3)
        self.assertEqual(term.abstract(), self.t3.abstract())

        term = self.t4.store_container((0, 0), (5, 3, 1))
        self.assertEqual(term.abstract(), self.t3.abstract())
        self.assertEqual(term, self.t3)

    def test_abstract3(self):
        t1 = Terminal(
            (
                Block(
                    (
                        Stack(((3, 3, 1),)),
                        Stack(())
                    ), False
                ),
            ), 4
        )

        t2 = Terminal(
            (
                Block(
                    (
                        Stack(()),
                        Stack(())
                    ), False
                ),
            ), 4
        )
        term = t2.store_container((0, 1), (5, 3, 1))
        self.assertNotEqual(term.abstract(), t1.abstract())

        term = t2.store_container((0, 0), (5, 4, 1))
        self.assertNotEqual(term.abstract(), t1.abstract())

    def test_abstract4(self):
        t: Terminal = Terminal(
            (
                # block 1
                Block(
                    (
                        Stack(((3, 3, -1),)),
                        Stack(())
                    ), False
                ),
                # block 2
                Block((
                    Stack(()),
                ), False
                ),
                # block 3
                Block((
                    Stack(()),
                ), True
                ),
                # block 4
                Block(
                    (
                        Stack(((10, 1, 1),)),
                        Stack(())
                    ), False
                ),
                # block 5
                Block(
                    (
                        Stack(()),
                        Stack(())
                    ), True
                ),
                # block 6
                Block(
                    (
                        Stack(((1, 1, 2),)),
                        Stack(())
                    ), True
                )
            ), 4
        )
        # order: 2, 3, 4, 1, 5, 6
        # order: 2,4,1,3,5,6

        t_abstract: Terminal = Terminal(
            (
                # block 2
                Block((
                    Stack(()),
                ), False
                ),
                # block 4
                Block(
                    (
                        Stack(((0, 1, 1),)),
                        Stack(())
                    ), False
                ),
                # block 1
                Block(
                    (
                        Stack(((0, 3, -1),)),
                        Stack(())
                    ), False
                ),
                # block 3
                Block((
                    Stack(()),
                ), True
                ),
                # block 5
                Block(
                    (
                        Stack(()),
                        Stack(())
                    ), True
                ),
                # block 6
                Block(
                    (
                        Stack(()),
                        Stack(((0, 1, 2), ))
                    ), True
                )
            ), 4
        )
        self.assertNotEqual(t, t_abstract)
        self.assertEqual(t.abstract(), t_abstract)

    def test_reveal1(self):
        t1 = Terminal(
            (
                Block(
                    (
                        Stack(((1, 1, 1),)),
                    ), False
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
                        Stack(((1, 1, 1),)),
                    ), False
                ),
                Block(
                    (
                        Stack(((2, 2, -1),)),
                    ), False
                )
            ), 4
        )

        self.assertEqual(t1, self.t1.reveal_order(((1, 1, -1),)))
        self.assertEqual(t2, self.t2.reveal_order(((1, 1, -1),)))

    def test_reveal2(self):
        term = self.t1.store_container((0, 0), (2, 1, -1))
        term = term.store_container((1, 0), (3, 1, -1))

        t = Terminal(
            (
                Block(
                    (
                        Stack(((1, 1, 2), (2, 1, 3))),
                    ), False
                ),
                Block(
                    (
                        Stack(((3, 1, 1),)),
                    ), False
                )
            ), 4
        )

        self.assertEqual(t, term.reveal_order(((3, 1, 1), (1, 1, 1), (2, 1, 1))))

    def test_find_container(self):
        self.assertEqual(self.t1.container_location((1, 1, -1)), (0, 0, 0))
        self.assertEqual(self.t1.container_location((1, 1, 1)), (0, 0, 0))

        self.assertEqual(self.t2.container_location((2, 2, -1)), (1, 0, 0))

        c = (3, 3, -1)
        self.assertEqual(self.t1.store_container((0, 0), c).container_location(c), (0, 0, 1))
        self.assertEqual(self.t1.store_container((1, 0), c).container_location(c), (1, 0, 0))
