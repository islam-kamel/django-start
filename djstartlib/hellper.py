import os
import click
import subprocess
import platform
import sys
def warn_stdout(message):
    print(f"⚠️ \033[93mWARNING: {message}\033[0m")

def create_env(env_name_path):
    click.secho("\U0001F984 Create Environment...", fg='blue')
    subprocess.call(
        f"{sys.executable} -m venv {env_name_path}",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        shell=True
    )
    if platform.system() == "Windows":
        os.environ.setdefault('PYTHONPATH', f"{env_name_path}{os.sep}Scripts{os.sep}python.exe")
        os.environ.setdefault('DJANGOADMIN', f"{env_name_path}{os.sep}Scripts{os.sep}django-admin.exe")
    else:
        os.environ.setdefault('PYTHONPATH', f"{env_name_path}{os.sep}Scripts{os.sep}python3")
        os.environ.setdefault('DJANGOADMIN', f"{env_name_path}{os.sep}Scripts{os.sep}django-admin.exe")
