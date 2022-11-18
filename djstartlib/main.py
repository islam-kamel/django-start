#!/usr/bin/env python
import pathlib

import click

from models import DjangoStart


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
@click.option("-v", "--virtualenv", is_flag=True, help="Install Environment Is Deprecated")
@click.option('-u', '--url-path', help='Set Custom URL Path for your App')
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
        click.secho("Creating a virtual environment is a best practice!",
                    fg="green")

    app = DjangoStart(
        kwargs['name'],
        app=kwargs['app_name'],
        project=kwargs['project_name']
    )

    app.setup_project()
    app.setup_app(app_url=kwargs['url_path'] or '')


if __name__ == "__main__":
    main()
