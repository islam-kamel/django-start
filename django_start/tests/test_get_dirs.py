import unittest
from django_start.utils.helpers import get_dirs


class TestGetDirs(unittest.TestCase):
    def test_get_dirs(self):
        result = get_dirs("venv")
        self.assertIn("Scripts", result)

    def test_get_dirs_not_found(self):
        with self.assertRaises(FileNotFoundError):
            get_dirs("tests_not_found")

    def test_get_dirs_full_path(self):
        result = get_dirs("venv", full_path=True)
        self.assertIn("venv\\Scripts", result)

    def test_get_dirs_return_type(self):
        result = get_dirs("venv")
        self.assertIsInstance(result, list)
