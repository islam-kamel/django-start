import sys
import urllib.error
from urllib import request
import json

version = "1.0.4"


def latest_version():
    res = request.urlopen("https://api.github.com/repos/islam-kamel/django-start/tags")
    version_name = json.load(res)[0]["name"]
    version_name = version_name.split(".")
    version_name[-1] = version_name[-1].split("-")[0]
    version_name = [int(num) for num in version_name]
    return version_name


def current_version():
    return [1, 0, 3]


def check_available():
    try:
        online = latest_version()
        current = current_version()
        if sum(online) > sum(current):
            return True
        else:
            return False
    except urllib.error.URLError:
        sys.exit(1)
        pass
