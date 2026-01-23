import os
import ollama
import json

from api.v1.recipe.constants import LLM_SCHEMA


class LLMService:
    """
    сервис для работы с LLM
    """

    def __init__(self):
        self.client = ollama.Client(host=os.getenv("HOST"))
        self.model = os.getenv("MODEL")
    
    def llm_json(self, prompt: str) -> dict:
        full_prompt = f"""
                        You are extracting data from a recipe text.
                        Return ONLY valid JSON strictly according to the schema.
                        No text outside of JSON.

                        Rules:
                        - if meal_type is explicitly mentioned in the text — use it
                        - if meal_type is not mentioned — try to determine it from context (ingredients, description, steps)
                        - do not invent ingredients

                        Schema:
                        {LLM_SCHEMA}

                        Request:
                        {prompt}
                    """
        
        response = self.client.chat(
            model=self.model,
            messages=[{
                "role": "user",
                "content": full_prompt
            }],
            options={
                "temperature": 0.1,
                "num_ctx": 2048,
                "repeat_penalty": 1.1,
            }
        )

        content = self._extract_json(response["message"]["content"])

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON from LLM: {content}")

    def _extract_json(self, content: str) -> str:
        content = content.strip()
        
        if content.startswith("```"):
            content = content.strip("`")
            if content.lower().startswith("json"):
                content = content[4:].strip()
        content = content.replace("'", '"')

        return content
