import os

import click

from models.utils import Environment
from models.utils.hellper import (build_view_func, build_views_urls,
                                  executable_python_command, generate_html,
                                  warn_stdout)


class AppManager(Environment):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.__app_name = kwargs.get('app', None)
        self.__workdir = os.path.join(
            self.get_workdir(),
            f'{self.get_app_name()}'
        )
        self.__views = os.path.join(self.workdir, 'views.py')
        self.__urls = os.path.join(self.workdir, 'urls.py')
        self.__templates = os.path.join(self.workdir, 'templates')
        self.python = os.getenv('PYTHONEXEC')
        self.__line_list = []

    @property
    def app_name(self) -> str:
        return self.__app_name

    @property
    def workdir(self) -> str:
        return self.__workdir

    @property
    def views(self) -> str:
        return self.__views

    @property
    def urls(self) -> str:
        return self.__urls

    @property
    def line_list(self) -> list:
        return self.__line_list

    @line_list.setter
    def line_list(self, value: str) -> None:
        self.__line_list = value

    def index(self, value: str) -> int:
        return self.line_list.index(value)

    def read_file(self, file: str) -> list:
        with open(file) as f:
            self.line_list = f.readlines()
            f.close()
        return self.line_list

    def update_lines_list(self, flag: str, value: str) -> None:
        self.line_list.insert(self.index(flag), value)

    def replace_line(self, index: int, value: str) -> None:
        self.line_list[index] = value

    def create_app(self) -> None:
        if self.app_name not in os.listdir(self.get_workdir()):
            click.secho(f"\U00002728 Create '{self.app_name}' App...",
                        fg="blue")
            executable_python_command(f"manage.py startapp {self.app_name}")
        else:
            warn_stdout(f'"{self.app_name}" already exist!')

    def update_view(self) -> None:
        self.read_file(self.views)
        if "# Create your views here.\n" in self.line_list:
            click.secho(f"\U0001F304 Create '{self.app_name}' Views...",
                        fg="blue")
            code_of_block = build_view_func().substitute(
                app_name=self.app_name, html_file="index.html"
            )
            self.replace_line(
                self.index("# Create your views here.\n"),
                code_of_block
            )
            with open(self.views, "w") as f:
                f.write("".join(self.line_list))
                f.close()
        else:
            warn_stdout('"home" View is Exists!')

    def create_urls(self) -> None:
        with open(self.urls, "w") as f:
            click.secho(f"\U0001F517 Create {self.app_name} URLs...",
                        fg="blue")
            block_of_code = build_views_urls().substitute(view_name="home")
            f.write(block_of_code)
            f.close()

    def create_templates(self) -> None:
        click.secho(f"\U0001F389 Generate '{self.app_name}' Index Page...",
                    fg="blue")

        if not os.path.exists(self.__templates):
            os.mkdir(self.__templates)

        self.__templates += f"{os.sep}{self.app_name}"
        if not os.path.exists(self.__templates):
            os.mkdir(self.__templates)

        with open(f"{self.__templates}{os.sep}index.html", "w") as f:
            f.write(generate_html())
            f.close()
