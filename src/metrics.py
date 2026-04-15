from __future__ import annotations

import re

from rapidfuzz import fuzz


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def fact_coverage_score(required_facts: list[str], generated_email: str) -> float:
    """Returns fraction of required facts found in generated email."""
    if not required_facts:
        return 1.0

    email_norm = _normalize(generated_email)
    hit_count = 0
    for fact in required_facts:
        fact_norm = _normalize(fact)
        ratio = fuzz.partial_ratio(fact_norm, email_norm)
        token_overlap = _token_overlap_ratio(fact_norm, email_norm)

        if ratio >= 78 or token_overlap >= 0.6:
            hit_count += 1

    return round(hit_count / len(required_facts), 4)


def _token_overlap_ratio(fact: str, email: str) -> float:
    fact_tokens = {t for t in re.findall(r"[a-z0-9]+", fact) if len(t) > 2}
    if not fact_tokens:
        return 0.0
    email_tokens = set(re.findall(r"[a-z0-9]+", email))
    overlap = fact_tokens & email_tokens
    return len(overlap) / len(fact_tokens)


def format_quality_score(generated_email: str) -> float:
    """Deterministic format score (0-1): structure + concise length."""
    text = generated_email.strip()
    word_count = len(re.findall(r"\b\w+\b", text))

    checks = [
        1.0 if text.lower().startswith("subject:") else 0.0,
        1.0 if "\n\n" in text else 0.0,
        1.0 if 90 <= word_count <= 260 else 0.0,
        1.0 if _has_signoff(text) else 0.0,
    ]
    return round(sum(checks) / len(checks), 4)


def _has_signoff(text: str) -> bool:
    signoff_tokens = ["regards", "sincerely", "best", "thanks", "warm regards", "kind regards"]
    tail = text.lower()[-180:]
    return any(token in tail for token in signoff_tokens)


def combine_quality_scores(format_score: float, llm_quality_score: float) -> float:
    """Hybrid custom metric: deterministic format checks + LLM fluency/clarity score."""
    combined = 0.4 * format_score + 0.6 * llm_quality_score
    return round(combined, 4)
