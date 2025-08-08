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
        lang_prompts = {
            "en": {
                "system": "You are an expert Git commit message generator. Create concise, descriptive commit messages following conventional commits format when appropriate.",
                "instructions": "Generate a Git commit message based on the provided information",
                "diff_label": "Code changes",
                "branch_label": "Branch",
                "history_label": "Recent commit history for context",
                "guidelines": """
                    Guidelines:
                    - Use imperative mood (e.g., "Add", "Fix", "Update", not "Added", "Fixed", "Updated")
                    - Keep the subject line under 72 characters
                    - Use conventional commits format when appropriate (feat:, fix:, docs:, style:, refactor:, test:, chore:)
                    - Be specific about what changed
                    - Consider the branch name and commit history for context
                    - Focus on the 'why' and 'what', not the 'how'
                    - Return ONLY the commit message text, without any markdown formatting, code blocks
                    - Do not wrap the response in backticks or code blocks
                    - Provide just the plain text commit message
                """
            },
            "es": {
                "system": "Eres un experto generador de mensajes de commit de Git. Crea mensajes de commit concisos y descriptivos siguiendo el formato de commits convencionales cuando sea apropiado.",
                "instructions": "Genera un mensaje de commit de Git basado en la información proporcionada",
                "diff_label": "Cambios en el código",
                "branch_label": "Rama",
                "history_label": "Historial de commits recientes para contexto",
                "guidelines": """
                    Pautas:
                    - Usa modo imperativo (ej: "Agregar", "Corregir", "Actualizar", no "Agregado", "Corregido", "Actualizado")
                    - Mantén la línea de asunto bajo 72 caracteres
                    - Usa formato de commits convencionales cuando sea apropiado (feat:, fix:, docs:, style:, refactor:, test:, chore:)
                    - Sé específico sobre lo que cambió
                    - Considera el nombre de la rama y el historial de commits para contexto
                    - Enfócate en el 'por qué' y 'qué', no en el 'cómo'
                    - Devuelve SOLO el texto del mensaje de confirmación, sin formato Markdown, bloques de código.
                    - No encierre la respuesta entre comillas invertidas ni bloques de código.
                    - Proporciona solo el texto sin formato del mensaje de confirmación.
                """
            }
        }

        texts = lang_prompts.get(context.lang, lang_prompts["en"])

        prompt_parts = [
            texts["instructions"] + ":\n",
            f"**{texts['branch_label']}:** {context.branch_name}",
        ]

        if context.commit_history:
            prompt_parts.append(f"**{texts['history_label']}:**")
            prompt_parts.append(context.commit_history)
            prompt_parts.append("")

        prompt_parts.extend([
            f"**{texts['diff_label']}:**",
            "```diff",
            context.diff,
            "```",
            "",
            texts["guidelines"]
        ])

        prompt = "\n".join(prompt_parts)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": texts["system"]},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=150,
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
