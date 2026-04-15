from __future__ import annotations

import json
import re
from typing import Any

from groq import Groq

from .schemas import JudgeResponse


class GroqService:
    def __init__(self, api_key: str) -> None:
        self.client = Groq(api_key=api_key)

    def chat(self, model: str, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    def judge(self, model: str, messages: list[dict[str, str]], temperature: float = 0.0) -> JudgeResponse:
        raw = self.chat(model=model, messages=messages, temperature=temperature)
        parsed = self._extract_json(raw)
        return JudgeResponse.model_validate(parsed)

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?", "", text).strip()
            text = re.sub(r"```$", "", text).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, flags=re.DOTALL)
            if not match:
                raise
            return json.loads(match.group(0))
