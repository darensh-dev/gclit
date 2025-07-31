# gclit/cli/main.py

import typer
from gclit.cli.utils import handle_cli_errors
from gclit.container import container
from gclit.application.use_cases.generate_commit import GenerateCommitMessage
from gclit.application.use_cases.generate_pr_docs import GeneratePullRequestDocs
from gclit.cli.commands_config import config_app
from gclit.domain.models.common import Lang

app = typer.Typer()
app.add_typer(config_app, name="config")


LangOptions = typer.Option("en", "--lang", help="Language for the documentation")


@app.command()
@handle_cli_errors
def commit(
    auto: bool = typer.Option(False, help="Automate create commit"),
    lang: Lang = LangOptions
):
    use_case = GenerateCommitMessage(
        llm_provider=container.get_llm_provider(),
        git_provider=container.get_git_provier()
    )
    message = use_case.execute(lang)
    typer.echo(f"\n🔤 Generated commit message:\n\n{message}\n")

    if auto:
        import subprocess
        subprocess.run(["git", "commit", "-m", message])
        typer.echo("✅ Commit created.")


@app.command("pr")
@handle_cli_errors
def pr_docs(
    branch_from: str = typer.Option(None, "--from", help="Source branch for the PR"),
    branch_to: str = typer.Option(None, "--to", help="Target branch for the PR"),
    pr_number: int = typer.Option(None, "--pr", help="PR number to update"),
    lang: Lang = LangOptions
):
    """
    Generates or updates pull request documentation.

    Use --from and --to to generate a new PR doc,
    or use --pr to update an existing one.
    """
    use_case = GeneratePullRequestDocs(
        llm_provider=container.get_llm_provider(),
        git_provider=container.get_git_provier()
    )

    if pr_number:
        result = use_case.execute(pr_number=pr_number, lang=lang)
    elif branch_from and branch_to:
        result = use_case.execute(from_branch=branch_from, to_branch=branch_to, lang=lang)
    else:
        typer.echo("❌ Must provide either --from/--to or --pr.")
        raise typer.Exit(code=1)

    typer.echo(f"\n📌 Title:\n{result['title']}\n\n📝 Description:\n{result['body']}\n")


if __name__ == "__main__":
    app()
