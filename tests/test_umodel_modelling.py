from dataclasses import dataclass
from pprint import pprint
import typing
import unittest
from zxutil.umodel import UItem
from zxutil.umodel.attrs import UError, UKey, UPrimaryKey, UniqueKey

UID_MUST_BE_AT_LEAST_7 = lambda x : len(x) == 7
VALID_EMAIL = lambda x : "@" in x and not x.startswith("@") and not x.endswith("@")

class modelling(unittest.TestCase):
    def test_1(self):
        
        @dataclass
        class test(UItem):
            uid : typing.Union[int, UPrimaryKey, UID_MUST_BE_AT_LEAST_7]
            name : typing.Union[str, UniqueKey]
            age : typing.Union[int, UKey]
            address : typing.Union[str, UKey]
            phone : typing.Union[int, UniqueKey]
            email : typing.Union[str, UniqueKey, VALID_EMAIL]

        pprint(test.get_stats())

@dataclass
class testx(UItem):
    uid : typing.Union[int, UPrimaryKey, UID_MUST_BE_AT_LEAST_7]
    name : typing.Union[str, UniqueKey]
    age : typing.Union[int, UKey]

class test(unittest.TestCase):
    def test_1(self):
        x = testx(
            uid=1234555,
            name="hello",
            age=12,
        )
        # test if primary key has been casted to str
        self.assertEqual(x.uid, "1234555")

        # test if primary key can't be changed
        with self.assertRaises(UError):
            x.uid = "12345"
        # test cannot create an item with same primary key
        with self.assertRaises(UError):
            testx(
                uid="1234555",
                name="pass",
                age=12,
            )
        # test cannot create an item with same unique key name
        with self.assertRaises(UError):
            testx(
                uid="1234566",
                name="hello",
                age=12,
            )
        # test
        testx(
            uid="1234566",
            name="pass",
            age=12,
        )
        data =test.export_all()
        pprint(data)
        self.assertEqual(len(data), 2)
        
        # test remove
        testx.remove(uid="1234566")
        data =test.export_all()
        pprint(data)
        self.assertEqual(len(data), 1)

    def test_2(self):
        x = testx(
            uid=1234555,
            name="hello",
            age=12,
        )
        y = testx(
            uid=1234566,
            name="pass",
            age=12,
        )
        z = testx(
            uid=1234577,
            name="someone",
            age=12,
        )

        pulled = testx.get(uid="1234566")
        self.assertIsNotNone(pulled)
        self.assertEqual(pulled.name, "pass")