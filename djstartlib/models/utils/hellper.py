import os
import click
import subprocess
import platform
import sys
from string import Template


def warn_stdout(message):
    print(f"⚠️ \033[93mWARNING: {message}\033[0m")


def create_env(env_name_path):
    click.secho("\U0001F984 Create Environment...", fg="blue")
    subprocess.call(
        f"{sys.executable} -m venv {env_name_path}",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        shell=True,
    )
    if platform.system() == "Windows":
        os.environ['PYTHONEXEC'] = os.path.join(env_name_path, 'Scripts/python.exe') 
        os.environ.setdefault('DJANGOADMIN', os.path.join(env_name_path, 'Scripts/django-admin.exe'))
    else:
        os.environ['PYTHONEXEC'] = os.path.join(env_name_path, 'bin/python3')
        os.environ.setdefault('DJANGOADMIN', os.path.join(env_name_path, 'bin/django-admin'))


def executable_python_command(command):
    try:
        proc = subprocess.call(
            f"{os.getenv('PYTHONEXEC')} {command}",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            shell=True,
        )
        if proc:
            if platform.system() != 'Windows':
                click.secho("check your installed python3-env and python3-pip", fg="white", bg="red")
            sys.exit(1)
    except KeyError:
        click.secho("Be sure to set up PYTHONPATH", fg="white", bg="red")
        sys.exit(1)


def executable_django_command(command):
    try:
        proc = subprocess.call(
            f"{os.getenv('DJANGOADMIN')} {command}",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            shell=True,
        )
        if proc:
            sys.exit(1)
    except KeyError:
        click.secho("Be sure to set up DJANGOADMIN", fg="white", bg="red")
        sys.exit(1)


def upgrade_pip():
    executable_python_command("-m pip install --upgrade pip")


def install_dep():
    executable_python_command("-m pip install django")


def requirements_extract():
    executable_python_command("-m pip freeze > requirements.txt")


def build_view_func():
    """
    :param
    app_name
    html_file
    :return: str
    """
    s = Template(f"""
def home(request):
    return render(request, '$app_name{os.sep}$html_file')""")
    return s


def build_views_urls():
    s = Template("""from django.urls import path
from . import views

urlpatterns = [
    path('', views.$view_name)
]"""
    )
    return s


def generate_html():
    """
    :return:
    Html Code
    """

    s = """<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Django Start</title>
        <style>
            *{text-align: center}
            div{display:flex; justify-content:center}
        </style>
    </head>
    <body>
        <h1 style="text-align: center">Hello, Django-Start</h1>
        <a style="text-align: center" class="github-button" href="https://github.com/islam-kamel/django-start" data-color-scheme="no-preference: light; light: light; dark: dark;" data-size="large" data-show-count="true" aria-label="Star islam-kamel/django-start on GitHub">Django-Start</a>
    </body>
    <script async defer src="https://buttons.github.io/buttons.js"></script>
</html>"""
    return s
