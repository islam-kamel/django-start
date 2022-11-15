#!/usr/bin/env python
import pathlib

import click

# from models.djstart_interface import DjangoStart
from models import AppManager
from models import ProjectManager
from models import DjangoStart
from models.utils.hellper import create_env
"""
from models.utils.hellper import create_env
from models.app_manager import AppManager
from models.project_manager import ProjectManager
"""
"""
from djstart_interface import DjangoStart
from hellper import create_env
from app_manager import AppManager
from project_manager import ProjectManager
"""
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

    # create_env(kwargs["name"])
    app = DjangoStart(kwargs['name'], app=kwargs['app_name'], project=kwargs['project_name'])
    app.setup_project()
    app.setup_app()
    """
    django_start = DjangoStart(
        app_name=kwargs["app_name"], core_name=kwargs["project_name"]
    )
    django_start.setup_project()
    django_start.setup_app()
    """

if __name__ == "__main__":
    main()
