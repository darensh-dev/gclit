# gclit/cli/main.py
import typer
from gclit.domain.models.common import Lang
from gclit.container import container
from gclit.cli.utils import handle_cli_errors
from gclit.application.use_cases.generate_commit import GenerateCommitMessage
from gclit.application.use_cases.generate_pr_docs import GeneratePullRequestDocs
from gclit.cli.config import config_app
import subprocess

app = typer.Typer()
app.add_typer(config_app, name="config")

LangOptions = typer.Option("en", "--lang", help="Language for the documentation")


@app.command()
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


def _display_pr_documentation(title: str, body: str):
    """Helper para mostrar la documentación generada"""
    typer.echo(f"\n{'='*60}")
    typer.echo(f"📌 TÍTULO DEL PR:")
    typer.secho(f"{title}", fg=typer.colors.BRIGHT_CYAN, bold=True)
    typer.echo(f"\n📝 DESCRIPCIÓN:")
    typer.echo(f"{body}")
    typer.echo(f"{'='*60}\n")


def _confirm_action(action_type: str) -> bool:
    """Helper para pedir confirmación"""
    return typer.confirm(f"¿Deseas {action_type} el Pull Request?")


@app.command("pr")
@handle_cli_errors
def pr_docs(
    branch_from: str = typer.Option(None, "--from", help="Source branch for the PR"),
    branch_to: str = typer.Option(None, "--to", help="Target branch for the PR"),
    pr_number: int = typer.Option(None, "--pr", help="PR number to update"),
    auto: bool = typer.Option(False, "--auto", help="Skip confirmation prompt"),
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

    # Validar parámetros
    if not pr_number and (not branch_from or not branch_to):
        typer.echo("❌ Must provide either --from/--to or --pr.")
        raise typer.Exit(code=1)

    # Ejecutar generación inicial
    result = use_case.execute(
        from_branch=branch_from,
        to_branch=branch_to,
        pr_number=pr_number,
        lang=lang,
        auto_confirm=auto
    )

    # Manejar errores
    if "error" in result:
        typer.secho(f"❌ {result['error']}", fg=typer.colors.RED)
        if result.get("dry_run"):
            _display_pr_documentation(result.get("title", ""), result.get("body", ""))
        raise typer.Exit(code=1)

    # Mostrar documentación generada
    _display_pr_documentation(result["title"], result["body"])

    # Feature 4: Si es dry_run (no acceso remoto), solo mostrar
    if result.get("dry_run") and not result.get("remote_available", True):
        typer.secho("ℹ️  No se pudo acceder al PR remoto. Documentación generada usando ramas locales.",
                    fg=typer.colors.YELLOW)
        return

    # Feature 3: Manejar confirmación
    if result.get("requires_confirmation"):
        action_type = "actualizar" if pr_number else "crear"
        if not _confirm_action(action_type):
            typer.echo("❌ Operación cancelada.")
            return

        # Ejecutar después de confirmación
        final_result = use_case.confirm_and_execute(
            from_branch=branch_from or result.get("from_branch"),
            to_branch=branch_to or result.get("to_branch"),
            title=result["title"],
            body=result["body"],
            pr_number=pr_number
        )

        if "error" in final_result:
            typer.secho(f"❌ Error: {final_result['error']}", fg=typer.colors.RED)
            return

        result = final_result

    # Mostrar resultado final
    if result.get("action") == "created":
        typer.secho(f"✅ Pull Request creado: {result.get('pr_url')}", fg=typer.colors.GREEN)
    elif result.get("action") == "updated":
        typer.secho(f"✅ Pull Request #{result.get('pr_number')} actualizado.", fg=typer.colors.GREEN)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
