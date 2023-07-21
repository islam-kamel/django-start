import typer

app = typer.Typer(add_completion=False)


@app.command()
def create():
    print(f"Django-Start Version 2.0.0 ✨")


if __name__ == "__main__":
    app()
