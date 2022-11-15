import os

import click

from models.utils import Environment
from models.utils.hellper import (executable_django_command, install_dep,
                                  requirements_extract, upgrade_pip,
                                  warn_stdout)


class ProjectManager(Environment):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.__urls = os.path.join(
            self.get_workdir(), f'{self.get_project_name()}/urls.py'
        )
        self.__settings = os.path.join(
            self.get_workdir(), f'{self.get_project_name()}/settings.py'
        )
        self.__other_dependencies = []
        self.__line_list = []

    @property
    def urls_path(self) -> str: return self.__urls

    @property
    def settings_path(self) -> str: return self.__settings

    @property
    def line_list(self) -> list: return self.__line_list

    def index(self, value: str) -> int: return self.__line_list.index(value)

    def update_lines_list(self, flag: str, value: str) -> None:
        self.__line_list.insert(self.index(flag), value)

    def replace_line(self, index, value) -> None:
        self.__line_list[index] = value

    @line_list.setter
    def line_list(self, value: list) -> None:
        self.__line_list = value

    def read_file(self, file: str) -> list:
        with open(file) as f:
            self.__line_list = f.readlines()
            f.close()
        return self.__line_list

    def update_settings(self) -> None:
        self.read_file(self.settings_path)
        if f"\t'{self.get_app_name()}',\n" not in self.__line_list:
            click.secho("\U0001F527 Update Project Settings...", fg="blue")
            self.update_lines_list("]\n", f"\t'{self.get_app_name()}',\n")
            with open(self.settings_path, "w") as f:
                f.write("".join(self.__line_list))
                f.close()
        else:
            warn_stdout(f'"{self.get_app_name()}" is installed!')

    def update_urls(self) -> None:
        self.read_file(self.urls_path)
        view_path = f"\tpath('', include('{self.get_app_name()}.urls')),\n"
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
    def upgrade_pip() -> None:
        click.secho("\U0001F4E6 Upgrade Pip...", fg="blue")
        upgrade_pip()

    @staticmethod
    def install_dep() -> None:
        click.secho("\U000023F3 Install Dependencies...", fg="blue")
        install_dep()

    @staticmethod
    def requirements_extract() -> None:
        click.secho("\U0001F4C3 Generate Requirements.txt...", fg="blue")
        requirements_extract()

    def create_project(self) -> None:
        if self.get_project_name() not in os.listdir(self.get_workdir()):
            click.secho(f"\U00002728 Create '{self.get_project_name()}' Project", fg="blue")
            executable_django_command(f"startproject {self.get_project_name()} .")
        else:
            warn_stdout(f'"{self.get_project_name()}" Already exist!')
