import unittest
from django_start.automate.settings import Settings


class TestSettings(unittest.TestCase):

    def setUp(self):
        self.working_dir = "C:\\Users\\User\\Desktop\\django_start\\tests"
        self.settings = Settings(working_dir=self.working_dir)

    def test_working_dir(self):
        self.assertEqual(self.settings.working_dir, self.working_dir)

    def test_working_dir_not_equal(self):
        self.assertNotEqual(self.settings.working_dir, "C:\\Users\\User\\Desktop\\django_start\\test")
