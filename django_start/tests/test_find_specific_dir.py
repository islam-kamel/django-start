import os
import unittest
from django_start.utils.helpers import find_specific_dir

sep = os.sep


class TestFindGetSpecificDir(unittest.TestCase):

    def test_find_specific_dir(self):
        result = find_specific_dir("venv", ["Scripts"])
        print(result)
        self.assertEqual(result, os.path.normpath("venv/Scripts"))

    def test_find_specific_dir_not_found(self):
        result = find_specific_dir("./venv", ["Scripts"])
        self.assertEqual(result, os.path.normpath("./venv/Scripts"))

    def test_find_specific_dir_return_type(self):
        result = find_specific_dir("./venv", ["Scripts"])
        self.assertIsInstance(result, str)
