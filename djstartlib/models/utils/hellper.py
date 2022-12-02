import os
import platform
import subprocess
import sys
from string import Template

import click

HTML = """<!DOCTYPE html>
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

PATTERNS = Template("""from django.urls import path
from . import views

urlpatterns = [
    path('', views.$view_name)
]""")

VIEW_FUNC = Template(f"""
def home(request):
    return render(request, r'$app_name{os.sep}$html_file')""")


def warn_stdout(message):
    print(f"⚠️  \033[93mWARNING: {message}\033[0m")


def print_status(msg):
    click.secho(msg, fg="blue")


def build_view_func():
    return VIEW_FUNC


def build_views_urls():
    return PATTERNS


def generate_html():
    return HTML


def create_env(env):
    click.secho("\U0001F984 Create Environment...", fg="blue")

    subprocess.call(
        f"{sys.executable} -m venv {env}",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        shell=True,
    )

    if platform.system() == "Windows":
        os.environ["PYTHONEXEC"] = os.path.join(env, "Scripts/python.exe")
        os.environ.setdefault(
            "DJANGOADMIN", os.path.join(env, "Scripts/django-admin.exe")
        )
    else:
        os.environ["PYTHONEXEC"] = os.path.join(env, "bin/python3")
        os.environ.setdefault("DJANGOADMIN", os.path.join(env, "bin/django-admin"))


def executable_python_command(command):
    try:
        proc = subprocess.call(
            f"{os.getenv('PYTHONEXEC')} {command}",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            shell=True,
        )
        if proc:
            msg = "check your internet connection or installed python3-env and python3-pip"
            if platform.system() != "Windows":
                click.secho(msg, fg="white", bg="red")
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
