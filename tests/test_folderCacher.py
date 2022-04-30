from zxutil.folderCacher import FolderCacher 
import unittest



class test(unittest.TestCase):
    def setUp(self) -> None:
        self.fc = FolderCacher("tests/test_folderCacher", True)

    def tearDown(self) -> None:
        # remove folder
        self.fc.remove_path()

    def test_cacher_1(self):
        lines = "whatever, this is a test"
        
        lines2 ="hello world"
        
        lines3 = "whos calling the fleet"

        self.fc.save(lines, "test_1")
        self.fc.save(lines2, "test_2")

        self.assertEqual(self.fc.load("test_1"), lines)
        self.assertEqual(self.fc.load("test_2"), lines2)

        self.fc.save(lines3, "test_1", overwrite=True)

        self.assertEqual(self.fc.load("test_1"), lines3)