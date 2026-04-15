from __future__ import annotations

from src.metrics import combine_quality_scores, fact_coverage_score, format_quality_score


def test_fact_coverage_full_match() -> None:
    facts = ["Invoice INV-3321 is overdue by 14 days", "Outstanding amount is 4200 USD"]
    email = """
    Subject: Payment Reminder

    Dear Customer,
    Invoice INV-3321 is overdue by 14 days. The outstanding amount is 4200 USD.
    Regards,
    AR Team
    """
    assert fact_coverage_score(facts, email) == 1.0


def test_fact_coverage_partial_match() -> None:
    facts = ["PO-8742 delayed by 9 days", "impacting plant line 3"]
    email = """
    Subject: Update

    PO-8742 is delayed and this is impacting plant line 3.
    Regards,
    Ops
    """
    score = fact_coverage_score(facts, email)
    assert 0.5 <= score <= 1.0


def test_format_quality_score() -> None:
    email = """
    Subject: Meeting Follow-Up

    Dear Team,
    Thank you for your time today. We will send the proposal by Friday.
    Best regards,
    Alex
    """
    assert format_quality_score(email) >= 0.75


def test_combine_quality_scores() -> None:
    assert combine_quality_scores(1.0, 0.5) == 0.7
