import sys
import subprocess
import urllib.error
from urllib import request
import json
import click
import importlib.metadata
from packaging.version import Version

try:
    _pkg_version = importlib.metadata.version("django-start-automate")
except importlib.metadata.PackageNotFoundError:
    _pkg_version = "2.0.0a1"

version = f"{_pkg_version} (beta)"


def latest_version():
    res = request.urlopen(
        "https://api.github.com/repos/islam-kamel/django-start/tags"
    )
    version_name = json.load(res)[0]["name"]
    version_obj = Version(version_name)
    return version_name, version_obj


def current_version():
    return Version(_pkg_version)


def check_available():
    try:
        var_name, var_version = latest_version()
        current = current_version()
        if var_version > current:
            print(f"New Update Available {var_name}")
            return True
        else:
            print("You have the latest version")

    except urllib.error.URLError:
        sys.exit(1)
        pass


@click.command()
@click.option("--update", is_flag=True, help="Install Latest Version")
@click.option("--check-update", is_flag=True, help="Check Update Available")
def main(update, check_update):
    """
    Display current version,
    and check for new updates and update django-start
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
