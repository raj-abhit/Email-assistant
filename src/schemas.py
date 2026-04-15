from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Tone = Literal["formal", "casual", "urgent", "empathetic"]


class Scenario(BaseModel):
    id: str
    intent: str
    tone: Tone
    key_facts: list[str]
    reference_email: str


class JudgeResponse(BaseModel):
    tone_alignment_score: float = Field(ge=0.0, le=1.0)
    professional_quality_score: float = Field(ge=0.0, le=1.0)
    tone_feedback: str
    quality_feedback: str


class EvaluatedCase(BaseModel):
    scenario_id: str
    strategy: str
    generation_model: str
    judge_model: str
    fact_coverage_score: float
    tone_alignment_score: float
    professional_quality_score: float
    overall_score: float
    generated_email: str
    tone_feedback: str
    quality_feedback: str


class RunSummary(BaseModel):
    strategy: str
    generation_model: str
    judge_model: str
    metric_definitions: dict[str, str]
    average_scores: dict[str, float]
    cases: list[EvaluatedCase]
