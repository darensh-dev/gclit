# gclit/cli/commands/commit.py

import typer
import subprocess
from gclit.domain.models.common import Lang
from gclit.container import container
from gclit.cli.options.common import LangOptions
from gclit.cli.utils import handle_cli_errors
from gclit.application.use_cases.generate_commit import GenerateCommitMessage

commit_app = typer.Typer()


@commit_app.command()
@handle_cli_errors
def commit(
    auto: bool = typer.Option(False, "--auto", help="Automatically create commit without confirmation"),
    lang: Lang = LangOptions
):
    """Generate a commit message based on staged changes."""
    use_case = GenerateCommitMessage(
        llm_provider=container.get_llm_provider(),
        git_provider=container.get_git_provier()
    )

    message = use_case.execute(lang)
    typer.echo(f"\n🔤 Generated commit message:\n")
    typer.secho(f"{message}", fg=typer.colors.BRIGHT_CYAN, bold=True)
    typer.echo()

    if auto:
        subprocess.run(["git", "commit", "-m", message])
        typer.secho("✅ Commit created automatically.", fg=typer.colors.GREEN)
    else:
        if typer.confirm("Do you want to create this commit?"):
            subprocess.run(["git", "commit", "-m", message])
            typer.secho("✅ Commit created.", fg=typer.colors.GREEN)
        else:
            typer.echo("❌ Commit cancelled.")


def register_commit_commands(app: typer.Typer):
    """Registra los comandos de commit en la aplicación principal"""
    app.add_typer(commit_app, name="commit", help="Commit message generation commands")
