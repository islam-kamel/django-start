import os
import black
from django_start.automate.settings import AppSettings
from django_start.automate.templates import HTML_TEMPLATE, VIEW_FUNC_TEMPLATE
from django_start.utils.helpers import run_command, create_dir, write_file


class DjangoApplication(AppSettings):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__html_name = "index.html"

    def create_django_app(self, path=''):
        """
        Create django app
        :param path: str
        :return: None
        """
        proc = run_command(f"django-admin startapp {self.app_name} {path}")

        if proc.returncode != 0:
            raise RuntimeError(f"Error while creating app {self.app_name}\n\tDetails: {proc.stderr}")

    def create_templates_dir(self):
        """
        Create templates dir
        :return: None
        """
        templates_dir = os.path.join(self.app_dir, "templates")

        create_dir(templates_dir)
        create_dir(os.path.join(templates_dir, self.app_name))

    def create_index_html(self):
        """
        Create index.html file
        :return: None
        """
        index_html = os.path.join(self.app_dir, "templates", self.app_name, "index.html")
        html = HTML_TEMPLATE

        write_file(index_html, html)

    def create_view_function(self):
        """
        Create view function
        :return: None
        """
        view_function = os.path.join(self.app_dir, "views.py")
        view = VIEW_FUNC_TEMPLATE.substitute(render_path=f"{self.app_name}/{self.__html_name}")
        view = black.format_str(view, mode=black.FileMode())

        write_file(view_function, view, force=True)
