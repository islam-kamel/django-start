import unittest
from django_start.utils.helpers import is_exist


class TestIsExist(unittest.TestCase):

    def test_is_exist(self):
        self.assertTrue(is_exist("django_start"))
        self.assertFalse(is_exist("django_start1"))
