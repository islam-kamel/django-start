import os
import subprocess
from hellper import warn_stdout
import click

class AppManager:
    def __init__(self, *args, **kwargs):
        self.__app_name = kwargs.get("app_name", None)
        self.__workdir = os.getcwd() + rf"{os.sep}{self.app_name}"
        self.__views = self.workdir + rf"{os.sep}views.py"
        self.__urls = self.workdir + rf"{os.sep}urls.py"
        self.__templates = self.workdir + f"{os.sep}templates"
        self.python = os.environ.get('PYTHONPATH', None)
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
            click.secho(f"\U00002728 Create '{self.app_name}' App...", fg='blue')
            subprocess.call(
                f"{self.python} manage.py startapp {self.app_name}", shell=True
            )
        else:
            warn_stdout(f'"{self.app_name}" already exist!')

    def update_view(self):
        self.read_file(self.views)
        if "# Create your views here.\n" in self.line_list:
            click.secho(f"\U0001F304 Create '{self.app_name}' View...", fg='blue')
            self.replace_line(
                self.index("# Create your views here.\n"),
                f"def home(request):\n\treturn render(request, '{self.app_name}{os.sep}index.html')\n",
            )
            with open(self.views, "w") as f:
                f.write("".join(self.line_list))
                f.close()
        else:
            warn_stdout('"home" View is already created!')

    def create_urls(self):
        with open(self.urls, "w") as f:
            click.secho(f"\U0001F517 Create {self.app_name} URLs...", fg='blue')
            # content = [
            #     "from django.urls import path\n",
            #     "from . import views\n" "\n",
            #     "urlpatterns = [\n",
            #     "\tpath('', views.home)\n" "]\n",
            # ]
            content = """
            from django.url import path
            from . import views
            urlpatterns = [
                path('', views.home)
            ]
            
            """
            f.write(content)
            f.close()

    def create_templates(self):
        click.secho(f"\U0001F389 Generate '{self.app_name}' Index Page...", fg='blue')

        if not os.path.exists(self.__templates):
            os.mkdir(self.__templates)
            self.__templates += f'{os.sep}{self.app_name}'
            os.mkdir(self.__templates)
        with open(f"{self.__templates}{os.sep}index.html", "w") as f:
            content = """
            <DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Django Start</title>
                </head>
                <body>
                    <h1 style="text-align: center"> Hello, Django-Start</h1>
                    <a class="github-button" href="https://github.com/islam-kamel/django-start" data-color-scheme="no-preference: light; light: light; dark: dark;" data-size="large" data-show-count="true" aria-label="Star islam-kamel/django-start on GitHub">Django-Start</a>
                <body>
                <script async defer src="https://buttons.github.io/buttons.js"></script>
            </html>
            """
            f.write(content)
            f.close()
