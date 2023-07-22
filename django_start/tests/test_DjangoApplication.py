import os
import shutil
import unittest
from django_start.automate.application import DjangoApplication


class TestDjangoApplication(unittest.TestCase):

    def setUp(self):
        self.app_name = "test_app"
        self.django_app = DjangoApplication(app_name=self.app_name)
        self.container = "./container"

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
        os.mkdir(self.container)
        self.django_app.create_django_app(self.container)
        self.assertTrue(os.path.isdir(self.container))

    def test_create_django_app_exception(self):
        with self.assertRaises(RuntimeError):
            self.django_app.create_django_app("notValidPath")

    def test_create_templates_dir(self):
        self.django_app.create_django_app()
        self.django_app.create_templates_dir()
        self.assertTrue(os.path.isdir(os.path.join(self.django_app.app_dir, "templates")))
        self.assertTrue(os.path.isdir(os.path.join(self.django_app.app_dir, "templates", self.app_name)))

        shutil.rmtree(self.django_app.app_dir)

    def test_create_index_html(self):
        self.django_app.create_django_app()
        self.django_app.create_templates_dir()
        self.django_app.create_index_html()
        self.assertTrue(os.path.isfile(os.path.join(self.django_app.app_dir, "templates", self.app_name, "index.html")))

    def test_create_view_function(self):
        self.django_app.create_django_app()
        self.django_app.create_view_function()
        self.assertTrue(os.path.isfile(os.path.join(self.django_app.app_dir, "views.py")))

        with open(os.path.join(self.django_app.app_dir, "views.py"), "r") as f:
            lines = f.readlines()
            self.assertEqual(lines[0], "from django.shortcuts import render\n")
            self.assertEqual(lines[1], "\n")
            self.assertEqual(lines[2], "\n")
            self.assertEqual(lines[3], "def index(request):\n")
            self.assertEqual(lines[4], f'    return render(request, "{self.app_name}/index.html")\n')

    def test_create_urls(self):
        self.django_app.create_django_app()
        self.django_app.create_urls()
        self.assertTrue(os.path.isfile(os.path.join(self.django_app.app_dir, "urls.py")))
        with open(os.path.join(self.django_app.app_dir, "urls.py"), "r") as f:
            lines = f.readlines()
            self.assertEqual(lines[0], "from django.urls import path\n")
            self.assertEqual(lines[1], "\n")
            self.assertEqual(lines[2], "from . import views\n")
            self.assertEqual(lines[3], "\n")
            self.assertEqual(lines[4], "urlpatterns = [\n")
            self.assertEqual(lines[5], '    path("", views.index, name="index"),\n')
            self.assertEqual(lines[6], "]\n")

    def tearDown(self) -> None:
        shutil.rmtree(self.django_app.app_dir, ignore_errors=True)
        shutil.rmtree(self.container, ignore_errors=True)
