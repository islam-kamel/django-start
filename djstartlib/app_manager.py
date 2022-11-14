import os
from hellper import (
    warn_stdout,
    executable_python_command,
    build_views_urls,
    build_view_func,
    generate_html,
)

import click


class AppManager:
    def __init__(self, *args, **kwargs):
        self.__app_name = kwargs.get("app_name", None)
        self.__workdir = os.getcwd() + rf"{os.sep}{self.app_name}"
        self.__views = self.workdir + rf"{os.sep}views.py"
        self.__urls = self.workdir + rf"{os.sep}urls.py"
        self.__templates = self.workdir + f"{os.sep}templates"
        self.python = os.environ.get("PYTHONPATH", None)
        self.__line_list = []

    @property
    def app_name(self):
        return self.__app_name

    @property
    def workdir(self):
        return self.__workdir

    @property
    def views(self):
        return self.__views

    @property
    def urls(self):
        return self.__urls

    @property
    def line_list(self):
        return self.__line_list

    @line_list.setter
    def line_list(self, value):
        self.__line_list = value

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

    def create_app(self):
        if self.app_name not in os.listdir(
            f"{os.sep}".join(self.workdir.split(os.sep)[:-1])
        ):
            click.secho(f"\U00002728 Create '{self.app_name}' App...", fg="blue")
            executable_python_command(f"manage.py startapp {self.app_name}")
        else:
            warn_stdout(f'"{self.app_name}" already exist!')

    def update_view(self):
        self.read_file(self.views)

        if "# Create your views here.\n" in self.line_list:
            click.secho(f"\U0001F304 Create '{self.app_name}' View...", fg="blue")
            code_of_block = build_view_func().substitute(
                app_name=self.app_name, html_file="index.html"
            )
            self.replace_line(self.index("# Create your views here.\n"), code_of_block)

            with open(self.views, "w") as f:
                f.write("".join(self.line_list))
                f.close()
        else:
            warn_stdout('"home" View is already created!')

    def create_urls(self):
        with open(self.urls, "w") as f:
            click.secho(f"\U0001F517 Create {self.app_name} URLs...", fg="blue")
            block_of_code = build_views_urls().substitute(view_name="home")
            f.write(block_of_code)
            f.close()

    def create_templates(self):
        click.secho(f"\U0001F389 Generate '{self.app_name}' Index Page...", fg="blue")

        if not os.path.exists(self.__templates):
            os.mkdir(self.__templates)

        self.__templates += f"{os.sep}{self.app_name}"
        if not os.path.exists(self.__templates):
            os.mkdir(self.__templates)
        with open(f"{self.__templates}{os.sep}index.html", "w") as f:
            f.write(generate_html())
            f.close()
