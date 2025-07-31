# cli/config.py
import typer
from gclit.config.settings import AppConfig, settings, get_config_keys

config_app = typer.Typer()

def key_autocomplete(ctx: typer.Context, args: list[str], incomplete: str):
    config = AppConfig.load()
    all_keys = get_config_keys(config)
    return [k for k in all_keys if k.startswith(incomplete)]


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., autocompletion=key_autocomplete),
    value: str = typer.Argument(...),
):
    """Actualiza una clave de configuración"""
    config = AppConfig.load()
    all_keys = get_config_keys(config)

    if key not in all_keys:
        typer.echo(f"❌ Clave inválida. Opciones disponibles: {', '.join(all_keys)}")
        raise typer.Exit(1)

    try:
        config.update(key, value)
        typer.echo(f"✅ '{key}' actualizado a '{value}'")
    except ValueError as e:
        typer.echo(f"❌ {str(e)}")

@config_app.command("show")
def config_show():
    """Muestra la configuración actual"""
    for key, value in settings.model_dump().items():
        typer.echo(f"{key}: {value}")
