# gclit/infrastructure/llm/openai_provider.py
import openai
from gclit.domain.models.commit_message import CommitContext
from gclit.domain.models.pull_request import PullRequestContext
from gclit.domain.ports.llm import LLMProvider

from pydantic import BaseModel, Field, ValidationError
from typing import Optional


class CommitMessageResponse(BaseModel):
    message: str = Field(
        ...,
        description="The generated commit message",
        max_length=72
    )


class PullRequestResponse(BaseModel):
    title: str = Field(
        ...,
        description="The pull request title",
        max_length=60
    )
    body: str = Field(
        ...,
        description="The pull request description in markdown format"
    )


class OpenAIWithFuncProvider(LLMProvider):
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

        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": texts["system"]},
                    {"role": "user", "content": prompt}
                ],
                response_format=CommitMessageResponse,
                temperature=0.3,
                max_tokens=150,
            )

            commit_response = response.choices[0].message.parsed
            return commit_response.message

        except ValidationError as e:
            # Fallback en caso de error de validación
            print(f"Validation error: {e}")
            return self._fallback_commit_message(context)
        except Exception as e:
            print(f"Error generating commit message: {e}")
            return self._fallback_commit_message(context)

    def generate_pr_documentation(self, context: PullRequestContext) -> dict:
        lang_prompts = {
            "en": {
                "system": "You are an expert Git assistant specialized in creating clear, actionable Pull Request documentation.",
                "title_guidelines": """
                    For the title:
                    - Create a specific, actionable title that describes WHAT was changed
                    - Use imperative mood (e.g., "Add user authentication", "Refactor payment processing")
                    - Keep it under 60 characters
                    - Be specific about the component/feature affected
                    - Avoid generic words like "update", "change", "modify"
                """,
                "description_guidelines": """
                    For the description:
                    - Start with a clear summary of the purpose/motivation
                    - List the most important technical changes
                    - Include any breaking changes or migration notes if applicable
                    - Use markdown formatting for readability
                """
            },
            "es": {
                "system": "Eres un experto asistente de Git especializado en crear documentación clara y accionable de Pull Requests.",
                "title_guidelines": """
                    Para el título:
                    - Crea un título específico y accionable que describa QUÉ se cambió
                    - Usa modo imperativo (ej: "Agregar autenticación de usuario", "Refactorizar procesamiento de pagos")
                    - Mantén menos de 60 caracteres
                    - Sé específico sobre el componente/característica afectada
                    - Evita palabras genéricas como "actualizar", "cambiar", "modificar"
                """,
                "description_guidelines": """
                    Para la descripción:
                    - Comienza con un resumen claro del propósito/motivación
                    - Lista los cambios técnicos más importantes
                    - Incluye cualquier cambio disruptivo o notas de migración si aplica
                    - Usa formato markdown para legibilidad
                """
            }
        }

        texts = lang_prompts.get(context.lang, lang_prompts["en"])

        prompt = f"""
            {texts["system"]}

            {texts["title_guidelines"]}

            {texts["description_guidelines"]}

            ### Context:
            - Language: {context.lang}
            - Source branch: `{context.from_branch}` 
            - Target branch: `{context.to_branch}`
            - Historical context: {context.commit_history if hasattr(context, 'commit_history') else 'Not available'}

            ### Git Diff:
            {context.diff}
        """

        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format=PullRequestResponse,
                temperature=0.3,
            )

            pr_response = response.choices[0].message.parsed
            return {
                "title": pr_response.title,
                "body": pr_response.body
            }

        except ValidationError as e:
            print(f"Validation error: {e}")
            return self._fallback_pr_documentation(context)
        except Exception as e:
            print(f"Error generating PR documentation: {e}")
            return self._fallback_pr_documentation(context)

    def _fallback_commit_message(self, context: CommitContext) -> str:
        """Fallback method for commit message generation"""
        return f"Update {context.branch_name.replace('-', ' ').replace('_', ' ')}"

    def _fallback_pr_documentation(self, context: PullRequestContext) -> dict:
        """Fallback method for PR documentation generation"""
        return {
            "title": f"Merge {context.from_branch} into {context.to_branch}",
            "body": f"## Changes\n\nMerging changes from `{context.from_branch}` into `{context.to_branch}`.\n\n## Context\n\nPlease review the diff for detailed changes."
        }
