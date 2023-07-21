import unittest
from django_start.utils.helpers import normalize_path


class TestNormalizePath(unittest.TestCase):
    def test_normalize_path(self):
        result = normalize_path("./venv")
        self.assertEqual(result, "venv")

    def test_normalize_path_return_type(self):
        result = normalize_path("venv")
        self.assertIsInstance(result, str)
