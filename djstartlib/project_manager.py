import os
import subprocess
import sys
from app_manager import AppManager
from hellper import warn_stdout


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
        return self.__line_list

    def index(self, value):
        return self.line_list.index(value)

    def read_file(self, file):
        with open(file) as f:
            self.line_list = f.readlines()
            f.close()
        return self.line_list

    def update_lines_list(self, flag, value):
        self.line_list.insert(self.index(flag), value)

    def replace_line(self, index, value):
        self.line_list[index] = value

    def update_settings(self):
        self.read_file(self.settings_path)
        if f"\t'{self.app_name}',\n" not in self.line_list:
            print("⚙️ Update Settings")
            self.update_lines_list("]\n", f"\t'{self.app_name}',\n")
            with open(self.settings_path, "w") as f:
                f.write("".join(self.line_list))
                f.close()
        else:
            warn_stdout(f'"{self.app_name}" is installed!')

    def update_urls(self):
        self.read_file(self.urls_path)
        view_path = f"\tpath('', include('{self.app_name}.urls')),\n"
        if view_path not in self.line_list:
            self.replace_line(
                self.index("from django.urls import path\n"),
                "from django.urls import path, include\n",
            )
            self.update_lines_list("]\n", view_path)
            with open(self.urls_path, "w") as f:
                f.write("".join(self.line_list))
                f.close()
        else:
            warn_stdout("Urls Already Updated")

    def install_dep(self):
        print("⏳ Install Dependencies")
        subprocess.call(
            f"{sys.executable} -m pip install django",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            shell=True,
        )

    def create_project(self):
        if self.core_name not in os.listdir(self.workdir):
            print(f'✨ Create Project "{self.core_name}"')
            subprocess.call(
                f"django-admin startproject {self.core_name} .", shell=True
            )
        else:
            warn_stdout(f'"{self.core_name}" already exist!')

    def requirements(self):
        print("🧾 Create Requirements.txt")
        subprocess.call(
            "pip freeze > requirements.txt",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            shell=True,
        )
