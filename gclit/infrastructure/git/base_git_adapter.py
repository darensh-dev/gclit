# gclit/infrastructure/git/base_git_adapter.py
import subprocess
from gclit.domain.ports.git import GitProvider


class BaseGitAdapter(GitProvider):
    def get_branch_name(self) -> str:
        cmd = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()

    def get_stash_diff(self) -> str:
        cmd = ["git", "diff", "--cached"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout

    def get_branch_diff(self, from_branch: str, to_branch: str) -> str:
        cmd = ["git", "diff", f"{to_branch}..{from_branch}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout

    def get_recent_commits(self, branch: str = None, limit: int = 5) -> str:
        """Obtiene los últimos commits para contexto histórico"""
        cmd = ["git", "log", f"-{limit}", "--oneline"]
        if branch:
            cmd.append(branch)

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()

    def create_commit(self, message: str) -> str:
        try:
            cmd = ["git", "commit", "-m", message]
            subprocess.run(cmd, capture_output=True, text=True, check=True)

            return "Commit created successfully"
            # hash_result = subprocess.run(
            #     ["git", "rev-parse", "HEAD"],
            #     capture_output=True,
            #     text=True
            # )
            # return {
            #     "success": True,
            #     "commit_hash": hash_result.stdout.strip()[:8],
            #     "message": f"Commit created successfully"
            # }
        except subprocess.CalledProcessError as e:
            return f"Failed to create commit: {e.stderr}"
            # return {
            #     "success": False,
            #     "message": f"Failed to create commit: {e.stderr}"
            # }
