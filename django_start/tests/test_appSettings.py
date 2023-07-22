import os
import shutil
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

    def test_create_django_app(self):
        self.app_settings.create_django_app()
        self.assertTrue(os.path.isdir(self.app_settings.app_dir))

        # check if is valid django app
        self.assertTrue(os.path.isfile(os.path.join(self.app_settings.app_dir, "admin.py")))
        self.assertTrue(os.path.isfile(os.path.join(self.app_settings.app_dir, "apps.py")))
        self.assertTrue(os.path.isfile(os.path.join(self.app_settings.app_dir, "models.py")))
        self.assertTrue(os.path.isfile(os.path.join(self.app_settings.app_dir, "tests.py")))
        self.assertTrue(os.path.isfile(os.path.join(self.app_settings.app_dir, "views.py")))
        self.assertTrue(os.path.isdir(os.path.join(self.app_settings.app_dir, "migrations")))
        self.assertTrue(os.path.isfile(os.path.join(self.app_settings.app_dir, "migrations", "__init__.py")))
        self.assertTrue(os.path.isfile(os.path.join(self.app_settings.app_dir, "__init__.py")))

        shutil.rmtree(self.app_settings.app_dir)

    def test_create_django_app_with_path(self):
        container = "./container"
        os.mkdir(container)
        self.app_settings.create_django_app(container)
        self.assertTrue(os.path.isdir(container))
        shutil.rmtree(container)

    def test_create_django_app_exception(self):
        with self.assertRaises(RuntimeError):
            self.app_settings.create_django_app("notValidPath")

    def tearDown(self):
        shutil.rmtree(self.app_settings.app_dir, ignore_errors=True)
