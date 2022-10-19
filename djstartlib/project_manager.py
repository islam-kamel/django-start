import os
import subprocess
import sys
import platform
from app_manager import AppManager
from hellper import warn_stdout
import click

class ProjectManager:
    def __init__(self, *args, **kwargs):
        self.__app_manager = AppManager(*args, **kwargs)
        self.__workdir = os.getcwd()
        self.__app_name = kwargs.get("app_name", None)
        self.__core_name = kwargs.get("core_name", None)
        self.__urls = (
            self.__workdir + rf"{os.sep}{self.core_name}{os.sep}urls.py"
        )
        self.__settings = (
            self.__workdir + rf"{os.sep}{self.core_name}{os.sep}settings.py"
        )
        self.__other_dependencies = []
        self.__line_list = []

    @property
    def app_manager(self):
        return self.__app_manager

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
        return self.line_list

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
            click.secho("\U0001F527 Update Project Settings...", fg='blue')
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
    def install_dep():
        click.secho("\U000023F3 Install Dependencies...", fg='blue')

        subprocess.call(
            f"{sys.executable} -m pip install django",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            shell=True,
        )

    @staticmethod
    def requirements_extract():
        click.secho("\U0001F4C3 Generate Requirements.txt...", fg='blue')
        subprocess.call(
            f"{sys.executable} -m pip freeze > requirements.txt",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            shell=True,
        )

    def create_project(self):
        if self.core_name not in os.listdir(self.workdir):
            click.secho(f"\U00002728 Create '{self.core_name}' Project", fg='blue')
            subprocess.call(
                f"django-admin startproject {self.core_name} .", shell=True
            )
        else:
            warn_stdout(f'"{self.core_name}" already exist!')

    def create_env(self, env_name_path):
        click.secho("\U0001F984 Create Environment...", fg='blue')
        subprocess.call(
            f"{sys.executable} -m venv {env_name_path}",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            shell=True,
        )
        if platform.system() == "Windows":
            sys.executable = (
                f"{env_name_path}{os.sep}Scripts{os.sep}python.exe"
            )
        else:
            sys.executable = f"{env_name_path}{os.sep}bin{os.sep}python3"
