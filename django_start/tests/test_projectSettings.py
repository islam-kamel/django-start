import os
import unittest
from django_start.automate.settings import ProjectSettings
from django_start.utils.helpers import create_dir


class TestProjectSettings(unittest.TestCase):

    def setUp(self) -> None:
        self.working_dir = os.getcwd()
        self.project_name = "test_project"
        self.project_settings = ProjectSettings(working_dir=self.working_dir, project_name=self.project_name)

    def test_working_dir(self):
        self.assertEqual(self.project_settings.working_dir, self.working_dir)

    def test_project_name(self):
        self.assertEqual(self.project_settings.project_name, self.project_name)

    def test_project_dir(self):
        self.assertEqual(self.project_settings.project_dir, os.path.join(self.working_dir, "test_project"))

    def test_project_dir_not_equal(self):
        self.assertNotEqual(self.project_settings.project_dir,
                            "C:\\Users\\User\\Desktop\\django_start\\tests\\test_project1")

    def test_project_exception(self):
        create_dir(self.project_settings.project_dir)

        with self.assertRaises(FileExistsError):
            ProjectSettings(working_dir=self.working_dir, project_name=self.project_name)

        os.rmdir(self.project_settings.project_dir)
