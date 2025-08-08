# gclit/application/use_cases/generate_pr_docs.py
from gclit.domain.exceptions.exception import GitProviderException
from gclit.domain.models.common import Lang
from gclit.domain.ports.llm import LLMProvider
from gclit.domain.models.pull_request import PullRequestContext, PullRequestInfo
from gclit.domain.ports.git import GitProvider

class GeneratePullRequestDocs:
    def __init__(self, llm_provider: LLMProvider, git_provider: GitProvider):
        self.llm_provider = llm_provider
        self.git_provider = git_provider

    def execute(
        self,
        from_branch: str = None,
        to_branch: str = None,
        pr_number: int = None, 
        lang: Lang = "en",
        auto_confirm: bool = False,
        dry_run: bool = False
    ) -> dict:
        
        if pr_number is not None:
            try:
                pr_data: PullRequestInfo = self.git_provider.get_pr_diff_by_number(pr_number)
                from_branch = pr_data.from_branch
                to_branch = pr_data.to_branch
                remote_available = True
            except Exception:
                remote_available = False
                if not from_branch or not to_branch:
                    raise GitProviderException("No se pudo obtener información del PR remoto y no se proporcionaron las ramas")

        try:
            diff = self.git_provider.get_branch_diff(from_branch, to_branch)
            if not diff:
                return {"error": "No hay diferencias entre las ramas especificadas"}
        except GitProviderException as e:
            if pr_number is not None:
                return {"error": f"No se pudo obtener el diff: {str(e)}. Usa --from y --to para especificar ramas locales"}
            raise e

        commit_history = self.git_provider.get_recent_commits(from_branch)

        context = PullRequestContext(
            diff=diff,
            from_branch=from_branch,
            to_branch=to_branch,
            lang=lang,
            commit_history=commit_history
        )

        result = self.llm_provider.generate_pr_documentation(context)
        
        if dry_run or (pr_number is not None and not remote_available):
            return {
                "title": result["title"],
                "body": result["body"],
                "dry_run": True,
                "remote_available": remote_available if pr_number else True
            }

        if not auto_confirm:
            return {
                "title": result["title"],
                "body": result["body"],
                "requires_confirmation": True
            }

        try:
            if pr_number is not None:
                self.git_provider.update_pr(pr_number, title=result["title"], body=result["body"])
                result["action"] = "updated"
                result["pr_number"] = pr_number
            else:
                pr_url = self.git_provider.create_pr(
                    from_branch=from_branch,
                    to_branch=to_branch,
                    title=result["title"],
                    body=result["body"]
                )
                result["action"] = "created"
                result["pr_url"] = pr_url
        except Exception as e:
            result["error"] = str(e)
            result["dry_run"] = True

        return result

    def confirm_and_execute(self, from_branch: str, to_branch: str, title: str, body: str, pr_number: int = None) -> dict:
        """Ejecuta la creación/actualización después de la confirmación"""
        try:
            if pr_number is not None:
                self.git_provider.update_pr(pr_number, title=title, body=body)
                return {"action": "updated", "pr_number": pr_number}
            else:
                pr_url = self.git_provider.create_pr(
                    from_branch=from_branch,
                    to_branch=to_branch,
                    title=title,
                    body=body
                )
                return {"action": "created", "pr_url": pr_url}
        except Exception as e:
            return {"error": str(e)}