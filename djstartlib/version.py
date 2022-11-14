import sys
import subprocess
import urllib.error
from urllib import request
import json
import click

version = "1.1.4 (beta)"


def latest_version():
    res = request.urlopen("https://api.github.com/repos/islam-kamel/django-start/tags")
    version_name = json.load(res)[0]["name"]
    version_int = version_name.split(".")
    version_int[-1] = version_int[-1].split("-")[0]
    version_int = [int(num) for num in version_int]
    return version_name, version_int


def current_version():
    return [1, 1, 4]


def check_available():
    try:
        ver_name, ver_int = latest_version()
        current = current_version()
        if sum(ver_int) > sum(current):
            print(f"New Update Available {ver_name}")
            return True

    except urllib.error.URLError:
        sys.exit(1)
        pass


@click.command()
@click.option("--update")
@click.option('--check-update')
def main(update, check_update):
    """
    Display current versio,
    check new update and update django-start
    """
    if check_update:
        return check_available()

    if update:
        return subprocess.call(
            f"{sys.executable} -m pip install --upgrade django-start-automate",
            shell=True,
        )

    print(version)


if __name__ == "__main__":
    main()
