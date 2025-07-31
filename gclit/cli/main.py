# gclit/cli/main.py

from enum import Enum
from typing import Literal
import typer
from gclit.container import container
from gclit.application.use_cases.generate_commit import GenerateCommitMessage
from gclit.application.use_cases.generate_pr_docs import GeneratePullRequestDocs
from gclit.cli.commands_config import config_app

app = typer.Typer()
app.add_typer(config_app, name="config")


class LangType(str, Enum):
    en = "en"
    es = "es"


LangOptions = typer.Option("en", "--lang", help="Language for the documentation")


@app.command()
def commit(
    auto: bool = typer.Option(False, help="Automate create commit"),
    lang: LangType = LangOptions
):
    use_case = GenerateCommitMessage(container.get_llm_provider())
    message = use_case.execute(lang)
    typer.echo(f"\n🔤 Generated commit message:\n\n{message}\n")

    if auto:
        import subprocess
        subprocess.run(["git", "commit", "-m", message])
        typer.echo("✅ Commit created.")


@app.command("pr")
def pr_docs(
    branch_from: str = typer.Option(None, "--from", help="Source branch for the PR"),
    branch_to: str = typer.Option(None, "--to", help="Target branch for the PR"),
    pr_number: int = typer.Option(None, "--pr", help="PR number to update"),
    lang: LangType = LangOptions
):
    """
    Generates or updates pull request documentation.

    Use --from and --to to generate a new PR doc,
    or use --pr to update an existing one.
    """
    use_case = GeneratePullRequestDocs(container.get_llm_provider())

    if pr_number:
        result = use_case.execute(pr_number=pr_number, lang=lang)
    elif branch_from and branch_to:
        result = use_case.execute(branch_from=branch_from, branch_to=branch_to, lang=lang)
    else:
        typer.echo("❌ Must provide either --from/--to or --pr.")
        raise typer.Exit(code=1)

    typer.echo(f"\n📌 Title:\n{result['title']}\n\n📝 Description:\n{result['body']}\n")


if __name__ == "__main__":
    app()
