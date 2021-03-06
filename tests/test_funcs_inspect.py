import unittest
import zxutils.inspect as inspecthack

class t1:
    @classmethod
    def test_1(cls):
        return inspecthack.caller_getattr("a")

class t2:
    def __init__(self) -> None:
        self.a = 10

    def test_1(self): 
        return t1.test_1()

def test_2():
    hello = 3
    a =101
    return t1.test_1()

class test(unittest.TestCase):
    def test_1(self):
        self.assertEqual(t2().test_1(), 10)

    def test_2(self):
        self.assertEqual(test_2(), 101)
