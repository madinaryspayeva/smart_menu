import os
import ollama
import json


class LLMService:
    """
    сервис для работы с LLM
    """

    def __init__(self):
        self.client = ollama.Client(host=os.getenv("HOST"))
        self.model = os.getenv("MODEL")
    
    def llm_json(self, prompt: str, schema_hint: str ) -> dict:
        full_prompt = f"""
                        Ты извлекаешь данные из текста рецепта.
                        Верни ТОЛЬКО валидный JSON строго по схеме.
                        Все дроби типа 1/2 преобразуй в десятичные числа, например 0.5.
                        Если данных нет — используй null или пустые массивы.
                        Никакого текста вне JSON.

                        Правила:
                        - unit и meal_type выбирай ТОЛЬКО из перечисленных значений
                        - если данные не указаны явно — используй null
                        - не придумывай ингредиенты

                        Схема:
                        {schema_hint}

                        Запрос:
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

        content = response["message"]["content"]
        content = self._extract_json(content)

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

