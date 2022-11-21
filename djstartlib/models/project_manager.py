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

    @property
    def urls_path(self) -> str: return self.__urls

    @property
    def settings_path(self) -> str: return self.__settings

    def update_settings(self) -> None:
        self.read_file(self.settings_path)
        if f"\t'{self.get_app_name()}',\n" not in self.line_list:
            click.secho("\U0001F527 Update Project Settings...", fg="blue")
            self.insert_line("]\n", f"\t'{self.get_app_name()}',\n")
            self.write(self.settings_path)
        else:
            warn_stdout(f'"{self.get_app_name()}" is installed!')

    def update_import_statment(self):
        import_statment = 'from django.urls import include\n'
        if 'from django.urls import path, include\n' in self.line_list:
            return 0
        elif import_statment not in self.line_list:
            self.insert_line('from django.urls import path\n', import_statment)

    def update_urls(self, path: str) -> None:
        self.read_file(self.urls_path)
        view_path = f"\tpath('{path}', include('{self.get_app_name()}.urls')),\n"
        self.update_import_statment()

        if view_path not in self.line_list:
            self.insert_line("]\n", view_path)
            self.write(self.urls_path)
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
