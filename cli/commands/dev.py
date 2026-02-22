"""Development commands."""

import subprocess
import sys

import typer
from rich.console import Console

app = typer.Typer(help="Development commands", invoke_without_command=True)
console = Console()


def run_cmd(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    console.print(f"[dim]$ {' '.join(cmd)}[/dim]")
    return subprocess.run(cmd, check=check)


@app.callback(invoke_without_command=True)
def dev_local(ctx: typer.Context):
    """Start local development environment."""
    if ctx.invoked_subcommand is not None:
        return

    console.print("[cyan]Starting local development environment...[/cyan]")
    try:
        run_cmd(["docker-compose", "up", "--build"])
    except subprocess.CalledProcessError:
        console.print("[red]Failed to start containers[/red]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping...[/yellow]")


@app.command("vps")
def dev_vps():
    """Start dev environment on VPS."""
    console.print("[cyan]Starting VPS dev environment...[/cyan]")
    try:
        run_cmd(["docker-compose", "-f", "docker-compose.dev.yml", "up", "-d", "--build"])
        console.print("[green]Dev environment started![/green]")
        console.print("[dim]Use 'python -m cli logs' to view logs[/dim]")
    except subprocess.CalledProcessError:
        console.print("[red]Failed to start containers[/red]")
        sys.exit(1)


def prod_cmd():
    """Start production environment."""
    console.print("[cyan]Starting production environment...[/cyan]")
    try:
        run_cmd(["docker-compose", "-f", "docker-compose.prod.yml", "up", "-d", "--build"])
        console.print("[green]Production environment started![/green]")
    except subprocess.CalledProcessError:
        console.print("[red]Failed to start containers[/red]")
        sys.exit(1)


def down_cmd():
    """Stop all containers."""
    console.print("[cyan]Stopping containers...[/cyan]")

    # Try to stop all possible environments
    for compose_file in ["docker-compose.yml", "docker-compose.dev.yml", "docker-compose.prod.yml"]:
        try:
            run_cmd(["docker-compose", "-f", compose_file, "down"], check=False)
        except Exception:
            pass

    console.print("[green]All containers stopped[/green]")


def logs_cmd(service: str | None = None, follow: bool = True):
    """Show container logs."""
    cmd = ["docker-compose", "logs"]

    if follow:
        cmd.append("-f")

    if service:
        cmd.append(service)

    try:
        run_cmd(cmd, check=False)
    except KeyboardInterrupt:
        pass


@app.command("build")
def build():
    """Build all containers."""
    console.print("[cyan]Building containers...[/cyan]")
    try:
        run_cmd(["docker-compose", "build"])
        console.print("[green]Build complete![/green]")
    except subprocess.CalledProcessError:
        console.print("[red]Build failed[/red]")
        sys.exit(1)


@app.command("restart")
def restart(service: str = typer.Argument(None, help="Service to restart")):
    """Restart containers."""
    cmd = ["docker-compose", "restart"]
    if service:
        cmd.append(service)

    console.print(f"[cyan]Restarting {'all services' if not service else service}...[/cyan]")
    try:
        run_cmd(cmd)
        console.print("[green]Restart complete![/green]")
    except subprocess.CalledProcessError:
        console.print("[red]Restart failed[/red]")
        sys.exit(1)


@app.command("ps")
def ps():
    """Show running containers."""
    run_cmd(["docker-compose", "ps"], check=False)
