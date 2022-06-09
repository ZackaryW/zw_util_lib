import os
from pprint import pprint
from zxutil.folder_cacher import FolderCacher
import unittest
from PIL.Image import Image


class test_webimg(unittest.TestCase):
    def setUp(self) -> None:
        self.fc = FolderCacher.make_webimg_cache("tests/test_cache_src", True, 'jpg')
        self.fc.MAX_HOLDING_QUEUE_SIZE = 2
        self.fc.MAX_CONSTANT_CACHE_SIZE = 2
        self.fc.MIN_REQ_TO_PLACE_CONSTANT = 2
    def test_cacher_1(self):
        
        img : Image = self.fc.load(
            key="0i0pen0p"
        )
        self.assertIsInstance(img, Image)

        self.fc.save("0000000", img)

        if os.path.exists("tests/test_cache_src/0000000.jpg"):
            os.remove("tests/test_cache_src/0000000.jpg")
        else:
            self.fail("File does not exist")

    def test_cacher_2(self):
        for x in range(0, 2):
            img : Image = self.fc.load(
            key="0i0pen0p"
        )

        for x in range(0, 1):
            img : Image = self.fc.load(
            key="2r5uovk8"
        )
        print(1)
        pprint(self.fc._holding_queue)
        pprint(self.fc._constant_cache)

        for x in range(0, 3):
            img : Image = self.fc.load(
            key="lreh0lxv"
        )

        print(2)
        pprint(self.fc._holding_queue)
        pprint(self.fc._constant_cache)


        for x in range(0, 3):
            img : Image = self.fc.load(
            key="2r5uovk8"
        )

        for x in range(0, 7):
            img : Image = self.fc.load(
            key="tguigl13"
        )

        for x in range(0, 2):
            img : Image = self.fc.load(
            key="w8k32nmy"
        )

        self.fc.load("tguigl13")
        pprint(self.fc.__dict__)
        self.assertEqual(len(self.fc._holding_queue), 2)
        self.assertEqual(len(self.fc._constant_cache), 2)
        self.assertTrue(["2r5uovk8", FolderCacher.CONSTANT_CACHE] in self.fc)
        self.assertTrue(["tguigl13", FolderCacher.CONSTANT_CACHE] in self.fc)
