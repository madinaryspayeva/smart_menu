import os
import ollama
import json
from json_repair import repair_json

from api.v1.recipe.constants import LLM_SCHEMA


class LLMService:
    """
    сервис для работы с LLM
    """

    def __init__(self):
        self.client = ollama.Client(host=os.getenv("HOST"))
        self.model = os.getenv("MODEL")
    
    def extract_recipe(self, raw_text: str) -> dict:
        prompt = f"""
                    You are given a raw transcript of a cooking video.
                    The text may contain speech recognition errors.

                    Your tasks:
                    1. Fix obvious transcription errors.
                    2. Extract structured recipe data.
                    3. Detect meal_type from context (breakfast, lunch, dinner, soup, dessert, drink, snack, baby_food, side_dish).

                    Rules:
                    - Do NOT invent ingredients.
                    - If meal type is unclear — choose the most appropriate based on context.
                    - If still unclear — use null.
                    - Return ONLY valid JSON.
                    - No explanations.
                    - No markdown.
                    - No text outside JSON.

                    Schema:
                    {LLM_SCHEMA}

                    Text:
                    {raw_text}
        """

        response = self.client.chat(
            model=self.model,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            options={
                "temperature": 0.1,
                "num_ctx": 2048,
                "num_predict": 700,    
                "repeat_penalty": 1.1,
            }
        )

        content = self._extract_json(response["message"]["content"])

        try:
            return json.loads(repair_json(content))
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON from LLM: {content}")

    def _extract_json(self, content: str) -> str:
        content = content.strip()

        if content.startswith("```"):
            content = content.strip("`").strip()
            if content.lower().startswith("json"):
                content = content[4:].strip()

        return content