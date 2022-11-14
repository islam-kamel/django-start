#!/usr/bin/env python
import pathlib

import click
from djstart_interface import DjangoStart
from hellper import create_env


@click.command()
@click.argument("project_name", type=str)
@click.argument("app_name", type=str)
@click.option(
    "-n",
    "--name",
    default="env",
    help="Custom Environment Name",
    type=lambda p: pathlib.Path(p).absolute(),
)
@click.option("-v", "--virtualenv", help="Install Environment Is Deprecated")
def main(**kwargs):
    """
    Prepare a new Django project quickly and automatically and,
    more wonderful things that save you time By django start
    """
    if kwargs["virtualenv"]:
        click.secho(
            "Please Don't Use This Option is Deprecated By Default Created Virtual Environment",
            fg="white",
            bg="red",
        )
        click.secho("Creating a virtual environment is a best practice!", fg="green")

    create_env(kwargs["name"])
    django_start = DjangoStart(
        app_name=kwargs["app_name"], core_name=kwargs["project_name"]
    )
    django_start.setup_project()
    django_start.setup_app()

if __name__ == "__main__":
    main()
