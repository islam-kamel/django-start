#! /usr/bin/python3
import sys
import subprocess
from djstartlib.djstart_interface import DjangoStart as djstart

try:
    import requests
except ModuleNotFoundError:
    print("⏳ Install Requirement Package")
    subprocess.call(
        "pip install requests",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        shell=True,
    )
    import requests


version = 3


def is_latest(api_ver, current_ver):
    pkg_ver, _ = api_ver.split("-")
    if "beta" in api_ver:
        beta_ver = api_ver.split("-")[1]
        pkg_ver = [int(x) for x in pkg_ver.split(".")]
        beta_vet = [int(x) for x in beta_ver.split(".")[1:]]
        return current_ver == sum(pkg_ver) + sum(beta_vet)
    return current_ver == sum(pkg_ver)


def check_update():
    url = "https://api.github.com/repos/islam-kamel/django-start/tags"
    token = "token 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"
    version_api = requests.get(
        url, headers={"Authorization": token}
    ).json()  # noqa E501
    latest = f'https://github.com/islam-kamel/django-start/releases/tag/{version_api[0]["name"]}'  # noqa E501
    if not is_latest(version_api[0]["name"], version):
        print(f"✨ \033[92mThere is a new version available: {latest}\033[0m")


def run():
    arguments = sys.argv
    app = djstart(core_name=arguments[1], app_name=arguments[2])
    app.setup_project()
    app.setup_app()


if __name__ == "__main__":
    sys.executable = "python"
    try:
        check_update()
        run()
    except IndexError:
        print("Fail Use ex. djagno-start <project_name> <app_name>")
