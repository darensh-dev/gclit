# gclit/cli/main.py
import typer
from gclit.cli.commands.commit import register_commit_commands
from gclit.cli.commands.pr import register_pr_commands
from gclit.cli.commands.config import register_config_app

app = typer.Typer(
    name="gclit",
    help="Git CLI assistant powered by LLMs for intelligent commit messages and pull request documentation.",
    no_args_is_help=True,
    add_completion=True,
)

register_commit_commands(app)
register_pr_commands(app)
register_config_app(app)


@app.command("version")
def version():
    """Show gclit version"""
    typer.echo("gclit version 0.1.0")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
