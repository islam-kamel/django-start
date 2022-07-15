#! /usr/bin/python3
import sys
import argparse
import pathlib
import re
from djstart_interface import DjangoStart as djstart

version = """
django-start 1.0.4 (Beta) automate start project and create app
"""


def check_regx(arg_value, pat=re.compile(r"^[a-zA-Z]")):
    if not pat.match(arg_value):
        return argparse.ArgumentParser.exit(1, "Enter valid name")
    else:
        return arg_value


def main():
    parser = argparse.ArgumentParser("django-start", description=version)
    parser.add_argument(
        "project_name", help="Write a project name", type=check_regx
    )
    parser.add_argument("app_name", help="Write an app name", type=check_regx)
    parser.add_argument(
        "-v", "--virtualenv", help="Create virtualenv", action="store_true"
    )
    parser.add_argument(
        "-n",
        "--name",
        default="env",
        const="env",
        type=lambda p: pathlib.Path(p).absolute(),
        nargs="?",
        metavar="",
        help="Set virtualenv name",
    )
    parser.add_argument(
        "path", type=lambda p: pathlib.Path(p).absolute(), help="select path"
    )
    args = parser.parse_args()
    if args.virtualenv:
        djstart.create_env(djstart, args.name)
    app = djstart(core_name=args.project_name, app_name=args.app_name)
    app.setup_project()
    app.setup_app()


if __name__ == "__main__":
    sys.executable = "python"
    main()
