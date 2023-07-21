import unittest
from django_start.utils.helpers import read_file


class TestReadFile(unittest.TestCase):
    def test_read_file(self):
        result = read_file("./django_start/tests/test_read_file.py")
        self.assertEqual(result[0], "import unittest\n")

    def test_read_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            read_file("./test_read_file_not_found.py")

    def test_read_file_return_type(self):
        result = read_file("./django_start/tests/test_read_file.py")
        self.assertIsInstance(result, list)
