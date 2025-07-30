# gclit/cli/main.py

import typer
from gclit.container import container
from gclit.application.use_cases.generate_commit import GenerateCommitMessage
from gclit.application.use_cases.generate_pr_docs import GeneratePullRequestDocs
from gclit.cli.commands_config import config_app

app = typer.Typer()
app.add_typer(config_app, name="config")


@app.command()
def commit(lang: str = "en", auto: bool = False):
    use_case = GenerateCommitMessage(container.get_llm_provider())
    message = use_case.execute(lang)
    typer.echo(f"\n🔤 Generated commit message:\n\n{message}\n")

    if auto:
        import subprocess
        subprocess.run(["git", "commit", "-m", message])
        typer.echo("✅ Commit created.")

@app.command("pr")
def pr_docs(
    branch_from: str = typer.Option(..., "--from"),
    branch_to: str = typer.Option(..., "--to"),
    lang: str = typer.Option("en", "--lang")
):
    use_case = GeneratePullRequestDocs(container.get_llm_provider())
    result = use_case.execute(branch_from, branch_to, lang)
    typer.echo(f"\n📌 Title:\n{result['title']}\n\n📝 Description:\n{result['body']}\n")

if __name__ == "__main__":
    app()
