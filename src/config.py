from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    gen_model_a: str
    gen_model_b: str
    judge_model: str
    temperature: float = 0.2



def load_settings() -> Settings:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Add it to your environment or .env file.")

    return Settings(
        groq_api_key=api_key,
        gen_model_a=os.getenv("GEN_MODEL_A", "llama-3.1-8b-instant"),
        gen_model_b=os.getenv("GEN_MODEL_B", "llama-3.3-70b-versatile"),
        judge_model=os.getenv("JUDGE_MODEL", "llama-3.1-8b-instant"),
    )
