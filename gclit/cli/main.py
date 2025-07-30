# cli/main.py
import typer
from application.use_cases.generate_commit import generate_commit_message
from config.config_manager import update_config, load_config

app = typer.Typer()
config_app = typer.Typer()
app.add_typer(config_app, name="config")

@config_app.command("set")
def set_config(key: str, value: str):
    """Set configuration value (e.g. gclit config set model gpt-4)"""
    update_config(key, value)
    typer.echo(f"✅ Config '{key}' updated to '{value}'")

@config_app.command("show")
def show_config():
    """Show current configuration"""
    config = load_config()
    for k, v in config.items():
        typer.echo(f"{k}: {v}")

@app.command()
def commit(lang: str = "en", auto: bool = False):
    message = generate_commit_message(lang=lang)
    typer.echo(f"\n🔤 Generated commit message:\n\n{message}\n")

    if auto:
        import subprocess
        subprocess.run(["git", "commit", "-m", message])
        typer.echo("✅ Commit created.")

if __name__ == "__main__":
    app()
