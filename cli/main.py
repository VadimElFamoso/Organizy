"""Main CLI application."""

import typer

from cli.commands import db, dev, init

app = typer.Typer(
    name="launchpad",
    help="Launchpad CLI - SaaS Starter toolkit",
    no_args_is_help=True,
)

# Add command groups
app.add_typer(init.app, name="init")
app.add_typer(dev.app, name="dev")
app.add_typer(db.app, name="db")


@app.command()
def down():
    """Stop all running containers."""
    dev.down_cmd()


@app.command()
def logs(
    service: str = typer.Argument(None, help="Service to show logs for (backend, frontend, postgres)"),
    follow: bool = typer.Option(True, "-f", "--follow", help="Follow log output"),
):
    """Show container logs."""
    dev.logs_cmd(service, follow)


@app.command()
def prod():
    """Start production environment."""
    dev.prod_cmd()


if __name__ == "__main__":
    app()
