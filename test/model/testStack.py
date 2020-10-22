import unittest

from main.model.dataclass.stack import Stack


class TestStack(unittest.TestCase):

    def test_equality(self):
        s1 = Stack.empty()
        s2 = Stack(())

        self.assertEqual(s1, s2)
        self.assertNotEqual(s1, s2.store_container((1, 1, -1)))

    def test_abstract_stack(self):
        s1 = Stack(((1, 1, -1),))
        s2 = Stack(((1, 1, 1),))
        s3 = Stack(((2, 1, -1),))
        s4 = Stack(((2, 1, 1),))

        self.assertEqual(s1.abstract(), s3.abstract())
        self.assertEqual(s2.abstract(), s4.abstract())
        self.assertEqual(s1, s3)
        self.assertEqual(s2, s4)

        self.assertNotEqual(s1, s2)
        self.assertNotEqual(s2, s3)

    def test_store(self):
        s = Stack.empty()
        s2 = Stack(((1, 1, -1),))
        s3 = Stack(((1, 1, -1), (2, 2, -1),))

        self.assertNotEqual(s, s2)
        self.assertNotEqual(s, s3)

        self.assertEqual(s.store_container((1, 1, -1)), s2)
        self.assertNotEqual(s.store_container((1, 1, -1)), s3)
        self.assertEqual(s.store_container((1, 1, -1)).store_container((2, 2, -1)), s3)
        self.assertNotEqual(s.store_container((1, 1, -1)).store_container((2, 2, -1)), s2)

    def test_retrieve(self):
        s2 = Stack(((1, 1, -1),))
        s3 = Stack(((1, 1, -1), (2, 2, -1),))

        stack, container = s3.retrieve_container()
        self.assertEqual(container, (2, 2, -1))
        self.assertNotEqual(container, (1, 1, -1))
        self.assertEqual(stack, s2)

        stack2, container2 = stack.retrieve_container()
        self.assertEqual(container2, (1, 1, -1))
        self.assertEqual(stack2, Stack.empty())

    def test_reveal(self):
        s = Stack(((1, 1, -1), (2, 2, -1),))
        s2 = Stack(((1, 1, 1), (2, 2, -1),))
        s3 = Stack(((1, 1, 2), (2, 2, 1),))

        self.assertEqual(s.reveal_order({1: 1}), s2)
        self.assertEqual(s.reveal_order({1: 2, 2: 1}), s3)


