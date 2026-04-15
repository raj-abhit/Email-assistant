from __future__ import annotations

from typing import Literal

from .schemas import Scenario

StrategyName = Literal["baseline", "fewshot"]


def build_generation_messages(scenario: Scenario, strategy: StrategyName) -> list[dict[str, str]]:
    facts_text = "\n".join(f"- {fact}" for fact in scenario.key_facts)

    if strategy == "baseline":
        system = (
            "You are a senior executive communications assistant. "
            "Write polished, professional emails with clear structure and concise language. "
            "Return only the email text."
        )
        user = f"""
Write an email using the details below.

Intent: {scenario.intent}
Tone: {scenario.tone}
Mandatory facts:
{facts_text}

Rules:
1) Include every mandatory fact exactly once in natural wording.
2) Include a clear subject line.
3) Keep length between 120 and 220 words.
4) Use a greeting and sign-off.
""".strip()
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    system = (
        "You are an enterprise email writing specialist. "
        "Follow the examples and constraints exactly, then produce one final email only."
    )
    few_shot_user = """
Example Input:
Intent: Confirm interview schedule
Tone: formal
Mandatory facts:
- Interview is on May 7 at 2:00 PM
- Format is virtual via Zoom
- Panel includes Product Lead and Engineering Manager
- Ask candidate to confirm availability
""".strip()
    few_shot_assistant = """
Subject: Interview Schedule Confirmation - May 7 at 2:00 PM

Dear Candidate,

Thank you for progressing to the next stage of our process. Your interview is scheduled for May 7 at 2:00 PM and will be conducted virtually via Zoom.

The interview panel will include our Product Lead and Engineering Manager. Please confirm your availability for this slot at your earliest convenience.

We look forward to speaking with you.

Best regards,
Hiring Team
""".strip()
    user = f"""
Now write the final email for this input.

Intent: {scenario.intent}
Tone: {scenario.tone}
Mandatory facts:
{facts_text}

Constraints:
- Include all mandatory facts.
- Match requested tone.
- Use subject, greeting, body, and sign-off.
- Keep it concise and professional.
Return only the final email.
""".strip()

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": few_shot_user},
        {"role": "assistant", "content": few_shot_assistant},
        {"role": "user", "content": user},
    ]


def build_judge_messages(intent: str, tone: str, key_facts: list[str], generated_email: str) -> list[dict[str, str]]:
    facts_text = "\n".join(f"- {fact}" for fact in key_facts)

    system = (
        "You are a strict evaluator for business email quality. "
        "Score only by rubric. Return valid JSON with keys: "
        "tone_alignment_score, professional_quality_score, tone_feedback, quality_feedback. "
        "Both scores must be numbers between 0 and 1."
    )
    user = f"""
Evaluate this generated email.

Intent: {intent}
Required Tone: {tone}
Required Facts:
{facts_text}

Generated Email:
{generated_email}

Rubric:
- tone_alignment_score: how well style matches the required tone.
- professional_quality_score: clarity, grammar, structure, and conciseness.

Output JSON only.
""".strip()

    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


METRIC_DEFINITIONS = {
    "fact_coverage_score": (
        "Deterministic metric (0-1): proportion of required facts recovered in generated email "
        "using token overlap + fuzzy similarity thresholds."
    ),
    "tone_alignment_score": (
        "LLM-as-a-judge metric (0-1): measures whether generated email tone matches requested tone "
        "(formal/casual/urgent/empathetic)."
    ),
    "professional_quality_score": (
        "Hybrid metric (0-1): weighted combination of deterministic format checks and "
        "LLM-judge rating for clarity, grammar, and conciseness."
    ),
}
