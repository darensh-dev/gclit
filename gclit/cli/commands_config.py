# cli/config.py
import typer
from gclit.config.settings import AppConfig, settings

config_app = typer.Typer()


@config_app.command("set")
def config_set(key: str, value: str):
    """Actualiza una clave de configuración"""
    config = AppConfig.load()
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
