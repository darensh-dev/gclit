# infrastructure/git/git_diff_provider.py
import subprocess

def get_git_diff(branch_from=None, branch_to=None) -> str:
    if branch_from and branch_to:
        cmd = ["git", "diff", f"{branch_from}..{branch_to}"]
    else:
        cmd = ["git", "diff", "--cached"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()
