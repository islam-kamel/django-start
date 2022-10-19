import sys
import subprocess
from project_manager import ProjectManager
import click


class DjangoStart(ProjectManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def upgrade_pip():
        click.secho("\U0001F4E6 Upgrade Pip...", fg='blue')
        subprocess.call(
            f"{sys.executable} -m pip install --upgrade pip",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            shell=True,
        )

    def setup_project(self):
        self.upgrade_pip()
        self.install_dep()
        self.create_project()
        self.requirements_extract()

    def setup_app(self):
        self.app_manager.create_app()
        self.update_settings()
        self.update_urls()
        self.app_manager.update_view()
        self.app_manager.create_templates()
        self.app_manager.create_urls()
