import os
import unittest
from django_start.automate.settings import AppSettings
from django_start.utils.helpers import create_dir


class TestAppSettings(unittest.TestCase):

    def setUp(self):
        self.working_dir = os.getcwd()
        self.app_name = "test_app"

        self.app_settings = AppSettings(working_dir=self.working_dir, app_name=self.app_name)

    def test_working_dir(self):
        self.assertEqual(self.app_settings.working_dir, self.working_dir)

    def test_app_name(self):
        self.assertEqual(self.app_settings.app_name, self.app_name)

    def test_app_dir(self):
        self.assertEqual(self.app_settings.app_dir, os.path.join(self.working_dir, self.app_name))

    def test_app_dir_not_equal(self):
        self.assertNotEqual(self.app_settings.app_dir, "C:\\Users\\User\\Desktop\\django_start\\tests\\test_app1")

    def test_app_exception(self):
        create_dir(self.app_settings.app_dir)

        with self.assertRaises(FileExistsError):
            AppSettings(working_dir=self.working_dir, app_name=self.app_name)

        os.rmdir(self.app_settings.app_dir)
