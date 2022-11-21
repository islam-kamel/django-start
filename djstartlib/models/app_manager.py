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

    @property
    def app_name(self) -> str:
        return self.__app_name

    @property
    def workdir(self) -> str:
        return self.__workdir

    @property
    def templates(self) -> str:
        return self.__templates

    @property
    def views(self) -> str:
        return self.__views

    @property
    def urls(self) -> str:
        return self.__urls

    def create_app(self) -> None:
        if self.app_name not in os.listdir(self.get_workdir()):
            click.secho(
                f"\U00002728 Create '{self.app_name}' App...",
                fg="blue"
            )
            executable_python_command(f"manage.py startapp {self.app_name}")
        else:
            warn_stdout(f'"{self.app_name}" already exist!')

    def update_view(self) -> None:
        click.secho(
            f"\U0001F304 Create '{self.app_name}' Views...",
            fg="blue"
        )

        self.read_file(self.views)
        if "# Create your views here.\n" in self.line_list:
            code_of_block = build_view_func().substitute(
                app_name=self.app_name,
                html_file="index.html"
            )
            self.replace_line(
                self.index("# Create your views here.\n"),
                code_of_block
            )
            self.write(self.views)

        else:
            warn_stdout('"home" View is Exists!')

    def create_urls(self) -> None:
        click.secho(
            f"\U0001F517 Create {self.app_name} URLs...",
            fg="blue"
        )

        block_of_code = build_views_urls().substitute(view_name="home")
        self.write(self.urls, value=block_of_code)

    def create_templates(self) -> None:
        click.secho(
            f"\U0001F389 Generate '{self.app_name}' Index Page...",
            fg="blue"
        )

        index_path = f'{self.templates}{os.sep}{self.app_name}'
        if not os.path.exists(self.templates):
            os.mkdir(self.templates)

        if not os.path.exists(index_path):
            os.mkdir(index_path)
            self.write(f'{index_path}{os.sep}index.html', value=generate_html())
        else:
            warn_stdout('Index.html is Already exists.')
