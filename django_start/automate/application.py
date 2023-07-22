from django_start.automate.settings import AppSettings
from django_start.utils.helpers import run_command


class DjangoApplication(AppSettings):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_django_app(self, path=''):
        """
        Create django app
        :param path: str
        :return: None
        """
        proc = run_command(f"django-admin startapp {self.app_name} {path}")

        if proc.returncode != 0:
            raise RuntimeError(f"Error while creating app {self.app_name}\n\tDetails: {proc.stderr}")
