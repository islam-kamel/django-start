import unittest
import os
from django_start.utils.helpers import write_file, is_exist, read_file


class TestWriteFile(unittest.TestCase):

    def test_write_file(self):
        write_file("test.txt", "test")
        self.assertTrue(is_exist("test.txt"))
        self.assertEqual(read_file("test.txt"), ["test"])
        os.remove("test.txt")
        self.assertFalse(is_exist("test.txt"))

    def test_write_file_force(self):
        write_file("test.txt", "test")
        write_file("test.txt", "test", force=True)
        self.assertEqual(read_file("test.txt"), ["test"])
        os.remove("test.txt")
        self.assertFalse(is_exist("test.txt"))

    def test_write_file_force_exception(self):
        write_file("test.txt", "test")

        with self.assertRaises(FileExistsError):
            write_file("test.txt", "test")

        os.remove("test.txt")
        self.assertFalse(is_exist("test.txt"))
