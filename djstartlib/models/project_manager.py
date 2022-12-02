import os

from models.utils import Environment
from models.utils.hellper import (
    executable_django_command,
    install_dep,
    print_status,
    requirements_extract,
    upgrade_pip,
    warn_stdout,
)


class ProjectManager(Environment):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.test()

    @property
    def urls_path(self) -> str:
        return self.join_path("urls.py")

    @property
    def settings_path(self) -> str:
        return self.join_path("settings.py")

    @staticmethod
    def upgrade_pip() -> None:
        print_status("\U0001F4E6 Upgrade Pip...")

        upgrade_pip()

    @staticmethod
    def install_dep() -> None:
        print_status("\U000023F3 Install Dependencies...")

        install_dep()

    @staticmethod
    def requirements_extract() -> None:
        print_status("\U0001F4C3 Generate Requirements.txt...")

        requirements_extract()

    def create_project(self) -> None:
        print_status(f"\U00002728 Create '{self.project_name}' Project")

        if self.project_name not in os.listdir(self.base_dir()):
            executable_django_command(f"startproject {self.project_name} .")
        else:
            warn_stdout(f'"{self.project_name}" Already exist!')

    def update_import_statment(self) -> None:
        import_statment = "from django.urls import include\n"

        if "from django.urls import path, include\n" in self.line_list:
            return
        elif import_statment not in self.line_list:
            self.insert_line("from django.urls import path\n", import_statment)

    def update_settings(self) -> None:
        print_status("\U0001F527 Update Project Settings...")

        self.read_file(self.settings_path)
        if f"\t'{self.app_name}',\n" not in self.line_list:
            self.insert_line("]\n", f"\t'{self.app_name}',\n")
            self.write(self.settings_path)
        else:
            warn_stdout(f'"{self.app_name}" is installed!')

    def update_urls(self, path: str) -> None:
        view_path = f"\tpath('{path}', include('{self.app_name}.urls')),\n"

        self.read_file(self.urls_path)
        self.update_import_statment()
        if view_path not in self.line_list:
            self.insert_line("]\n", view_path)
            self.write(self.urls_path)
        else:
            warn_stdout("Urls Already Updated")
