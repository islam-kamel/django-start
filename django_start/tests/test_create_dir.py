import os
import unittest
from django_start.utils.helpers import create_dir, is_exist


class TestCreateDir(unittest.TestCase):

    def test_create_dir(self):
        create_dir("test")
        self.assertTrue(is_exist("test"))
        os.rmdir("test")

    def test_create_dir_exception(self):
        with self.assertRaises(FileExistsError):
            create_dir("django_start")
