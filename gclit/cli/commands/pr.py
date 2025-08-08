# gclit/cli/commands/pr.py

import typer
from gclit.domain.models.common import Lang, LangOptions
from gclit.container import container
from gclit.cli.utils import handle_cli_errors
from gclit.application.use_cases.generate_pr_docs import GeneratePullRequestDocs

pr_app = typer.Typer()


def _display_pr_documentation(title: str, body: str):
    """Helper para mostrar la documentación generada"""
    typer.echo(f"\n{'='*60}")
    typer.echo(f"📌 PR TITLE:")
    typer.secho(f"{title}", fg=typer.colors.BRIGHT_CYAN, bold=True)
    typer.echo(f"\n📝 PR DESCRIPTION:")
    typer.echo(f"{body}")
    typer.echo(f"{'='*60}\n")


def _confirm_action(action_type: str) -> bool:
    """Helper para pedir confirmación"""
    return typer.confirm(f"Do you want to {action_type} the Pull Request?")


@pr_app.command("generate")
@handle_cli_errors
def generate(
    branch_from: str = typer.Option(None, "--from", help="Source branch for the PR"),
    branch_to: str = typer.Option(None, "--to", help="Target branch for the PR"),
    pr_number: int = typer.Option(None, "--pr", help="PR number to update"),
    auto: bool = typer.Option(False, "--auto", help="Skip confirmation prompt"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Generate documentation without creating/updating PR"),
    lang: Lang = LangOptions
):
    """
    Generate or update pull request documentation.

    Use --from and --to to generate a new PR doc,
    or use --pr to update an existing one.
    """
    use_case = GeneratePullRequestDocs(
        llm_provider=container.get_llm_provider(),
        git_provider=container.get_git_provier()
    )

    # Validar parámetros
    if not pr_number and (not branch_from or not branch_to):
        typer.secho("❌ Must provide either --from/--to or --pr.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Ejecutar generación inicial
    result = use_case.execute(
        from_branch=branch_from,
        to_branch=branch_to,
        pr_number=pr_number,
        lang=lang,
        auto_confirm=auto,
        dry_run=dry_run
    )

    # Manejar errores
    if "error" in result:
        typer.secho(f"❌ {result['error']}", fg=typer.colors.RED)
        if result.get("dry_run") and "title" in result:
            _display_pr_documentation(result.get("title", ""), result.get("body", ""))
        raise typer.Exit(code=1)

    # Mostrar documentación generada
    _display_pr_documentation(result["title"], result["body"])

    # Si es dry_run, solo mostrar resultado
    if dry_run or result.get("dry_run"):
        if not result.get("remote_available", True):
            typer.secho("ℹ️  Could not access remote PR. Documentation generated using local branches.",
                        fg=typer.colors.YELLOW)
        else:
            typer.secho("ℹ️  Dry run mode - no PR was created or updated.", fg=typer.colors.BLUE)
        return

    # Manejar confirmación
    if result.get("requires_confirmation"):
        action_type = "update" if pr_number else "create"
        if not _confirm_action(action_type):
            typer.echo("❌ Operation cancelled.")
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
        typer.secho(f"✅ Pull Request created: {result.get('pr_url')}", fg=typer.colors.GREEN)
    elif result.get("action") == "updated":
        typer.secho(f"✅ Pull Request #{result.get('pr_number')} updated.", fg=typer.colors.GREEN)


@pr_app.command("list")
@handle_cli_errors
def list_prs():
    """List open pull requests (future feature)"""
    typer.echo("🚧 Feature coming soon: List open PRs")


def register_pr_commands(app: typer.Typer):
    """Registra los comandos de PR en la aplicación principal"""
    app.add_typer(pr_app, name="pr", help="Pull Request documentation commands")
