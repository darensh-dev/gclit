# infrastructure/llm/openai_provider.py
import openai
from domain.models.commit_message import CommitContext
from domain.services.llm import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key

    def generate_commit_message(self, context: CommitContext) -> str:
        client = openai.OpenAI(api_key=self.api_key)

        prompt = (
            f"You are a helpful assistant. Generate a concise Git commit message "
            f"based on the following diff (language: {context.lang}).\n"
            f"Branch: {context.branch_name}\n\n"
            f"{context.diff}\n"
        )

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()
