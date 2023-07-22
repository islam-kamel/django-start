import os
import shutil
import unittest
from django_start.automate.application import DjangoApplication


class TestDjangoApplication(unittest.TestCase):

    def setUp(self):
        self.app_name = "test_app"
        self.django_app = DjangoApplication(app_name=self.app_name)

    def test_create_django_app(self):
        self.django_app.create_django_app()
        self.assertTrue(os.path.isdir(self.django_app.app_dir))

        # check if is valid django app
        self.assertTrue(os.path.isfile(os.path.join(self.django_app.app_dir, "admin.py")))
        self.assertTrue(os.path.isfile(os.path.join(self.django_app.app_dir, "apps.py")))
        self.assertTrue(os.path.isfile(os.path.join(self.django_app.app_dir, "models.py")))
        self.assertTrue(os.path.isfile(os.path.join(self.django_app.app_dir, "tests.py")))
        self.assertTrue(os.path.isfile(os.path.join(self.django_app.app_dir, "views.py")))
        self.assertTrue(os.path.isdir(os.path.join(self.django_app.app_dir, "migrations")))
        self.assertTrue(os.path.isfile(os.path.join(self.django_app.app_dir, "migrations", "__init__.py")))
        self.assertTrue(os.path.isfile(os.path.join(self.django_app.app_dir, "__init__.py")))

        shutil.rmtree(self.django_app.app_dir)

    def test_create_django_app_with_path(self):
        container = "./container"
        os.mkdir(container)
        self.django_app.create_django_app(container)
        self.assertTrue(os.path.isdir(container))
        shutil.rmtree(container)

    def test_create_django_app_exception(self):
        with self.assertRaises(RuntimeError):
            self.django_app.create_django_app("notValidPath")

    def tearDown(self):
        pass
