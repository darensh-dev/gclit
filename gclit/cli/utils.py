# gclit/cli/utils.py

import typer
from functools import wraps

from gclit.domain.exceptions.exception import GclitException, LLMProviderException


def handle_cli_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GclitException as e:
            typer.secho(f"❌ Error: {str(e)}", fg=typer.colors.RED)
        except LLMProviderException as e:
            typer.secho(f"❌ Error: {str(e)}", fg=typer.colors.RED)
        except Exception as e:
            typer.secho(f"💥 Error inesperado: {str(e)}", fg=typer.colors.BRIGHT_RED)

    return wrapper
