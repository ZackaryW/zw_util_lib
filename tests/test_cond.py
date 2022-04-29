from pprint import pprint
import unittest
import typing
from zxutil.cond import CondField, CondLex

class poc(unittest.TestCase):
    def test_typing(self):
        self.assertEqual(typing.get_origin(typing.List[str]), list)

        self.assertEqual(typing.get_origin(list), None)
        union_type_1 = typing.Union[str, int]
        self.assertEqual(typing.get_origin(union_type_1), typing.Union)
        self.assertEqual(typing.get_args(union_type_1), (str, int))


class test(unittest.TestCase):
    def test_cond_1(self):
        cfield = CondField(
            funcs=lambda x : x > 100,
            typ=int,
            range=(0, 150),
        )

        self.assertTrue(cfield.match(130))

    def test_cond_2(self):
        cfield = CondField(
            range=["hello", "world","123"],
            typ=str,
            funcs= lambda x : x.isdigit(),
        )
        self.assertTrue(cfield.match("123"))

    def test_cond_3(self):
        cfield = CondField(
            typ=str,
            funcs=lambda x : len(x) == 1
        )
        pprint(cfield.stats)
        self.assertFalse(cfield.match("hello"))
        self.assertTrue(cfield.match("c"))