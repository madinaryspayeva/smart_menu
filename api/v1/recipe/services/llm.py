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
    
    def normalize_text(self, text: str) -> str:
        prompt = f"""
                    You are given a raw transcript of a cooking video.
                    The text may contain speech recognition errors.

                    Task:
                    - restore correct words
                    - fix spelling and obvious transcription mistakes
                    - keep the original meaning
                    - preserve the original language
                    - output plain text only

                    Text:
                    {text}
                """
        
        response = self.client.chat(
            model=self.model,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            options={
                "temperature": 0.2,
                "num_ctx": 2048,
            }
        )

        return response["message"]["content"].strip()
    
    def llm_json(self, prompt: str) -> dict:
        full_prompt = f"""
                        You are extracting data from a recipe text. 
                        Return ONLY valid JSON strictly according to the schema. 
                        No text outside of JSON. 
                        Rules: 
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
