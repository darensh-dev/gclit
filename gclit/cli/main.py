# cli/main.py
import typer
from gclit.application.use_cases.generate_commit import generate_commit_message
from gclit.application.use_cases.generate_pr_docs import generate_pull_request_docs
from gclit.cli.commands_config import config_app


app = typer.Typer()
app.add_typer(config_app, name="config")


@app.command()
def commit(lang: str = "en", auto: bool = False):
    message = generate_commit_message(lang=lang)
    typer.echo(f"\n🔤 Generated commit message:\n\n{message}\n")

    if auto:
        import subprocess
        subprocess.run(["git", "commit", "-m", message])
        typer.echo("✅ Commit created.")


@app.command("pr")
def pr_docs(
    branch_from: str = typer.Option(..., "--from", help="Branch origen"),
    branch_to: str = typer.Option(..., "--to", help="Branch destino"),
    lang: str = typer.Option(None, "--lang", help="Idioma (default en config)")
):
    """Genera título + descripción de PR con IA"""
    result = generate_pull_request_docs(branch_from, branch_to, lang)
    typer.echo(f"\n📌 Title:\n{result['title']}\n\n📝 Description:\n{result['body']}\n")


if __name__ == "__main__":
    app()
