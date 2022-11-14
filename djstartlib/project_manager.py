import os
from app_manager import AppManager
from hellper import (
    warn_stdout,
    executable_django_command,
    install_dep,
    requirements_extract,
    upgrade_pip,
)
import click


class ProjectManager:
    def __init__(self, *args, **kwargs):
        self.__app_manager = AppManager(*args, **kwargs)
        self.__workdir = os.getcwd()
        self.__app_name = kwargs.get("app_name", None)
        self.__core_name = kwargs.get("core_name", None)
        self.__urls = self.__workdir + rf"{os.sep}{self.core_name}{os.sep}urls.py"
        self.__settings = (
            self.__workdir + rf"{os.sep}{self.core_name}{os.sep}settings.py"
        )
        self.python = os.environ.get("PYTHONPATH", None)
        self.django_admin = os.environ.get("DJANGOADMIN", None)
        self.__other_dependencies = []
        self.__line_list = []

    @property
    def app_manager(self):
        return self.__app_manager

    @property
    def python(self):
        return self.__python

    @python.setter
    def python(self, python_path):
        self.__python = python_path

    @property
    def django_admin(self):
        return self.__django_admin

    @django_admin.setter
    def django_admin(self, django_admin_path):
        self.__django_admin = django_admin_path

    @property
    def core_name(self):
        return self.__core_name

    @property
    def workdir(self):
        return self.__workdir

    @property
    def app_name(self):
        return self.__app_name

    @property
    def urls_path(self):
        return self.__urls

    @property
    def settings_path(self):
        return self.__settings

    @property
    def line_list(self):
        return self.__line_list

    @line_list.setter
    def line_list(self, value):
        self.__line_list = value

    def index(self, value):
        return self.__line_list.index(value)

    def read_file(self, file):
        with open(file) as f:
            self.__line_list = f.readlines()
            f.close()
        return self.__line_list

    def update_lines_list(self, flag, value):
        self.__line_list.insert(self.index(flag), value)

    def replace_line(self, index, value):
        self.__line_list[index] = value

    def update_settings(self):
        self.read_file(self.settings_path)
        if f"\t'{self.app_name}',\n" not in self.__line_list:
            click.secho("\U0001F527 Update Project Settings...", fg="blue")
            self.update_lines_list("]\n", f"\t'{self.app_name}',\n")
            with open(self.settings_path, "w") as f:
                f.write("".join(self.__line_list))
                f.close()
        else:
            warn_stdout(f'"{self.app_name}" is installed!')

    def update_urls(self):
        self.read_file(self.urls_path)
        view_path = f"\tpath('', include('{self.app_name}.urls')),\n"
        if view_path not in self.__line_list:
            self.replace_line(
                self.index("from django.urls import path\n"),
                "from django.urls import path, include\n",
            )
            self.update_lines_list("]\n", view_path)
            with open(self.urls_path, "w") as f:
                f.write("".join(self.__line_list))
                f.close()
        else:
            warn_stdout("Urls Already Updated")

    @staticmethod
    def upgrade_pip():
        click.secho("\U0001F4E6 Upgrade Pip...", fg="blue")
        upgrade_pip()

    @staticmethod
    def install_dep():
        click.secho("\U000023F3 Install Dependencies...", fg="blue")
        install_dep()

    @staticmethod
    def requirements_extract():
        click.secho("\U0001F4C3 Generate Requirements.txt...", fg="blue")
        requirements_extract()

    def create_project(self):
        if self.core_name not in os.listdir(self.workdir):
            click.secho(f"\U00002728 Create '{self.core_name}' Project", fg="blue")
            executable_django_command(f"startproject {self.core_name} .")
        else:
            warn_stdout(f'"{self.core_name}" already exist!')
