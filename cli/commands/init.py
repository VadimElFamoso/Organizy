"""Setup wizard command."""

import secrets
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

app = typer.Typer(help="Setup wizard for new projects", invoke_without_command=True)
console = Console()


def generate_jwt_secret() -> str:
    """Generate a secure JWT secret."""
    return secrets.token_hex(32)


@app.callback(invoke_without_command=True)
def init_wizard(ctx: typer.Context):
    """Interactive setup wizard to configure your Launchpad project."""
    if ctx.invoked_subcommand is not None:
        return

    console.print(Panel.fit(
        "[bold cyan]Launchpad Setup Wizard[/bold cyan]\n"
        "This will help you configure your project.",
        border_style="cyan"
    ))

    # Project settings
    console.print("\n[bold]Project Configuration[/bold]")

    project_name = Prompt.ask(
        "Project name",
        default="launchpad"
    )

    # Database
    console.print("\n[bold]Database Configuration[/bold]")

    db_password = Prompt.ask(
        "Database password",
        default=project_name,
        password=True
    )

    # Google OAuth
    console.print("\n[bold]Google OAuth Configuration[/bold]")
    console.print("[dim]Get credentials at: https://console.cloud.google.com/apis/credentials[/dim]")

    google_client_id = Prompt.ask(
        "Google Client ID",
        default=""
    )

    google_client_secret = Prompt.ask(
        "Google Client Secret",
        default="",
        password=True
    )

    # JWT
    console.print("\n[bold]JWT Configuration[/bold]")

    auto_generate_jwt = Confirm.ask(
        "Auto-generate JWT secret?",
        default=True
    )

    if auto_generate_jwt:
        jwt_secret = generate_jwt_secret()
        console.print(f"[green]Generated JWT secret: {jwt_secret[:16]}...[/green]")
    else:
        jwt_secret = Prompt.ask(
            "JWT Secret (min 32 chars)",
            password=True
        )

    # Stripe
    console.print("\n[bold]Stripe Configuration[/bold]")
    console.print("[dim]Get keys at: https://dashboard.stripe.com/apikeys[/dim]")

    enable_stripe = Confirm.ask(
        "Configure Stripe payments?",
        default=False
    )

    stripe_secret = ""
    stripe_webhook_secret = ""
    stripe_price_monthly = ""
    stripe_price_yearly = ""

    if enable_stripe:
        stripe_secret = Prompt.ask("Stripe Secret Key", default="sk_test_xxx")
        stripe_webhook_secret = Prompt.ask("Stripe Webhook Secret", default="whsec_xxx")
        stripe_price_monthly = Prompt.ask("Monthly Price ID", default="price_xxx")
        stripe_price_yearly = Prompt.ask("Yearly Price ID", default="price_xxx")

    # URLs
    console.print("\n[bold]URL Configuration[/bold]")

    domain = Prompt.ask(
        "Domain (for VPS deployment)",
        default=f"{project_name}.example.com"
    )

    # Generate .env content
    env_content = f"""# Environment: dev or prod
ENVIRONMENT=dev

# Database
POSTGRES_PASSWORD={db_password}

# Google OAuth
GOOGLE_CLIENT_ID={google_client_id}
GOOGLE_CLIENT_SECRET={google_client_secret}

# JWT Secret
JWT_SECRET_KEY={jwt_secret}

# Stripe
STRIPE_SECRET_KEY={stripe_secret}
STRIPE_WEBHOOK_SECRET={stripe_webhook_secret}
STRIPE_PRICE_ID_PRO_MONTHLY={stripe_price_monthly}
STRIPE_PRICE_ID_PRO_YEARLY={stripe_price_yearly}

# URLs (for VPS deployment)
DOMAIN={domain}
FRONTEND_URL=https://{domain}
GOOGLE_REDIRECT_URI=https://{domain}/api/v1/auth/google/callback
"""

    # Write .env file
    console.print("\n[bold]Writing configuration...[/bold]")

    env_path = Path(".env")
    if env_path.exists():
        overwrite = Confirm.ask(
            f"[yellow].env already exists. Overwrite?[/yellow]",
            default=False
        )
        if not overwrite:
            console.print("[yellow]Skipping .env file[/yellow]")
            return

    env_path.write_text(env_content)
    console.print(f"[green]Created .env file[/green]")

    # Summary
    console.print(Panel.fit(
        "[bold green]Setup complete![/bold green]\n\n"
        "Next steps:\n"
        "1. Review and edit .env if needed\n"
        "2. Run [cyan]python -m cli dev[/cyan] to start development\n"
        "3. Visit http://localhost:5173",
        border_style="green"
    ))
