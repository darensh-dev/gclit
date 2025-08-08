# gclit/infrastructure/llm/openai_provider.py
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
            You are an expert Git assistant specialized in creating clear, actionable Pull Request documentation.

            **IMPORTANT for the title:**
            - Create a specific, actionable title that describes WHAT was changed, not just "update" or "fix"
            - Use imperative mood (e.g., "Add user authentication", "Refactor payment processing", "Fix memory leak in parser")
            - Keep it under 60 characters
            - Be specific about the component/feature affected
            - Avoid generic words like "update", "change", "modify" unless they're the most accurate

            **For the description:**
            - Start with a clear summary of the purpose/motivation
            - List the most important technical changes (avoid formatting/whitespace noise)
            - Include any breaking changes or migration notes if applicable
            - Use markdown formatting for readability

            ### Context:
            - Language: {context.lang}
            - Source branch: `{context.from_branch}` 
            - Target branch: `{context.to_branch}`
            - Historical context: {context.commit_history if hasattr(context, 'commit_history') else 'Not available'}

            ### Git Diff:
            {context.diff}

            Please respond with:
            **Title:** [your specific, actionable title here]

            **Description:**
            [your markdown description here]
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Reducir temperatura para más consistencia
        )

        content = response.choices[0].message.content.strip()

        # Mejorar el parsing
        lines = content.split('\n')
        title = ""
        body_lines = []

        in_description = False
        for line in lines:
            if line.startswith('**Title:**'):
                title = line.replace('**Title:**', '').strip()
            elif line.startswith('**Description:**'):
                in_description = True
            elif in_description:
                body_lines.append(line)

        if not title:
            # Fallback: tomar la primera línea no vacía
            title = next((line.strip() for line in lines if line.strip()), "Update changes")

        body = '\n'.join(body_lines).strip()

        return {
            "title": title,
            "body": body
        }
