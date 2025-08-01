# infrastructure/llm/openai_provider.py
import openai
from gclit.domain.models.commit_message import CommitContext
from gclit.domain.models.pull_request import PullRequestContext
from gclit.domain.ports.llm import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_commit_message(self, context: CommitContext) -> str:

        prompt = (
            f"You are a helpful assistant. Generate a concise Git commit message "
            f"based on the following diff (language: {context.lang}).\n"
            f"Branch: {context.branch_name}\n\n"
            f"{context.diff}\n"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()

    def generate_pr_documentation(self, context: PullRequestContext) -> dict:

        prompt = f"""
            You are an expert Git assistant.

            Analyze the following Git diff and generate:
            1. A clear, concise, and specific Pull Request **title** (max 12 words), summarizing the main change or purpose.
            2. A Pull Request **description** in markdown with:
            - A short summary in plain English.
            - A list of the most important changes (avoid noise like formatting or comments).
            - Optional: include the motivation or context if the change addresses a specific problem or feature.

            Use the appropriate tone for a professional engineering team (avoid generic titles like "Pull Request Title").

            ### Context:
            - Branch: {context.branch_name}
            - Language: {context.lang}

            ### Diff:
            {context.diff}
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        content = response.choices[0].message.content.strip()

        # Simple split: assumes format "## Title\n\n## Description"
        title = content.split("\n")[0].replace("#", "").strip()
        body = "\n".join(content.split("\n")[1:]).strip()

        return {
            "title": title,
            "body": body
        }
