"""Database commands."""

import subprocess
import sys

import typer
from rich.console import Console
from rich.prompt import Confirm

app = typer.Typer(help="Database commands")
console = Console()


def run_cmd(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    console.print(f"[dim]$ {' '.join(cmd)}[/dim]")
    return subprocess.run(cmd, check=check)


@app.command("migrate")
def migrate():
    """Run database migrations."""
    console.print("[cyan]Running database migrations...[/cyan]")
    try:
        run_cmd([
            "docker-compose", "exec", "-T", "backend",
            "uv", "run", "alembic", "upgrade", "head"
        ])
        console.print("[green]Migrations complete![/green]")
    except subprocess.CalledProcessError:
        console.print("[red]Migration failed[/red]")
        sys.exit(1)


@app.command("reset")
def reset():
    """Reset database (WARNING: destroys all data)."""
    if not Confirm.ask(
        "[red]This will destroy all data. Are you sure?[/red]",
        default=False
    ):
        console.print("[yellow]Cancelled[/yellow]")
        return

    console.print("[cyan]Resetting database...[/cyan]")

    try:
        # Stop containers
        run_cmd(["docker-compose", "down", "-v"], check=False)

        # Start fresh
        run_cmd(["docker-compose", "up", "-d", "postgres"])

        console.print("[yellow]Waiting for database to be ready...[/yellow]")
        import time
        time.sleep(5)

        # Run migrations
        run_cmd(["docker-compose", "up", "-d", "backend"])
        time.sleep(3)

        run_cmd([
            "docker-compose", "exec", "-T", "backend",
            "uv", "run", "alembic", "upgrade", "head"
        ])

        console.print("[green]Database reset complete![/green]")
    except subprocess.CalledProcessError:
        console.print("[red]Reset failed[/red]")
        sys.exit(1)


@app.command("revision")
def revision(message: str = typer.Argument(..., help="Migration message")):
    """Create a new migration revision."""
    console.print(f"[cyan]Creating migration: {message}[/cyan]")
    try:
        run_cmd([
            "docker-compose", "exec", "-T", "backend",
            "uv", "run", "alembic", "revision", "--autogenerate", "-m", message
        ])
        console.print("[green]Migration created![/green]")
    except subprocess.CalledProcessError:
        console.print("[red]Failed to create migration[/red]")
        sys.exit(1)


@app.command("downgrade")
def downgrade(revision: str = typer.Argument("-1", help="Revision to downgrade to")):
    """Downgrade database to a previous revision."""
    if not Confirm.ask(
        f"[yellow]Downgrade to {revision}?[/yellow]",
        default=False
    ):
        console.print("[yellow]Cancelled[/yellow]")
        return

    console.print(f"[cyan]Downgrading to {revision}...[/cyan]")
    try:
        run_cmd([
            "docker-compose", "exec", "-T", "backend",
            "uv", "run", "alembic", "downgrade", revision
        ])
        console.print("[green]Downgrade complete![/green]")
    except subprocess.CalledProcessError:
        console.print("[red]Downgrade failed[/red]")
        sys.exit(1)


@app.command("shell")
def shell():
    """Open a database shell."""
    console.print("[cyan]Opening database shell...[/cyan]")
    console.print("[dim]Use \\q to exit[/dim]")
    try:
        subprocess.run([
            "docker-compose", "exec", "postgres",
            "psql", "-U", "launchpad", "-d", "launchpad"
        ])
    except subprocess.CalledProcessError:
        console.print("[red]Failed to open shell[/red]")
        sys.exit(1)
