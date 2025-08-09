# gclit/__init__.py
"""
gclit - Git CLI assistant powered by LLMs
"""

__version__ = "1.0.1"
__author__ = "Daren.dev"
__email__ = "sdaren6@gmail.com"
__description__ = "Git CLI assistant powered by LLMs for intelligent commit messages and pull request documentation"

from .cli.main import app

__all__ = ["app", "__version__"]