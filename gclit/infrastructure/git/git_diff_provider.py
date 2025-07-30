# infrastructure/git/git_diff_provider.py
import subprocess

def get_git_diff() -> str:
    result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
    return result.stdout.strip()
