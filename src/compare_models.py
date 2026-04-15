from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from .config import load_settings
from .data_loader import load_scenarios
from .evaluate import evaluate, save_outputs


def build_analysis_text(rows: list[dict], out_path: Path) -> Path:
    a, b = rows

    winner = a if a["overall_score"] >= b["overall_score"] else b
    loser = b if winner is a else a

    gap_fact = loser["fact_coverage_score"] - winner["fact_coverage_score"]
    gap_tone = loser["tone_alignment_score"] - winner["tone_alignment_score"]
    gap_quality = loser["professional_quality_score"] - winner["professional_quality_score"]

    failures: list[str] = []
    if gap_fact < 0:
        failures.append("missing required facts")
    if gap_tone < 0:
        failures.append("tone mismatch")
    if gap_quality < 0:
        failures.append("weaker professional quality")
    failure_text = ", ".join(failures) if failures else "no clear single failure mode"

    text = f"""# Comparative Analysis Summary

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Models / Strategies
- Candidate A: strategy={a['strategy']}, generation_model={a['generation_model']}
- Candidate B: strategy={b['strategy']}, generation_model={b['generation_model']}
- Judge Model: {a['judge_model']}

## Metric Results (Average)
- Candidate A: fact_coverage={a['fact_coverage_score']}, tone_alignment={a['tone_alignment_score']}, professional_quality={a['professional_quality_score']}, overall={a['overall_score']}
- Candidate B: fact_coverage={b['fact_coverage_score']}, tone_alignment={b['tone_alignment_score']}, professional_quality={b['professional_quality_score']}, overall={b['overall_score']}

## Which performed better?
{winner['label']} performed better overall with an average score of {winner['overall_score']}, compared to {loser['overall_score']}.

## Biggest failure mode of the lower-performing candidate
The primary observed failure mode for {loser['label']} was: {failure_text}.

## Production recommendation
Recommend {winner['label']} for production because it produced the highest overall score while maintaining stronger balance across all three custom metrics.
"""
    out_path.write_text(text, encoding="utf-8")
    return out_path


def build_generated_emails_text(summary_a, summary_b, out_path: Path) -> Path:
    scenarios = {s.id: s for s in load_scenarios()}
    cases_a = {c.scenario_id: c for c in summary_a.cases}
    cases_b = {c.scenario_id: c for c in summary_b.cases}

    lines: list[str] = []
    lines.append("# Generated Email Outputs")
    lines.append("")
    lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append(
        f"Candidate A: strategy={summary_a.strategy}, model={summary_a.generation_model}"
    )
    lines.append(
        f"Candidate B: strategy={summary_b.strategy}, model={summary_b.generation_model}"
    )
    lines.append("")

    for scenario_id in sorted(scenarios.keys()):
        scenario = scenarios[scenario_id]
        case_a = cases_a[scenario_id]
        case_b = cases_b[scenario_id]

        lines.append(f"## {scenario_id} - {scenario.intent}")
        lines.append(f"Tone: {scenario.tone}")
        lines.append("")
        lines.append("Required facts:")
        for fact in scenario.key_facts:
            lines.append(f"- {fact}")
        lines.append("")

        lines.append("### Human Reference Email")
        lines.append("```text")
        lines.append(scenario.reference_email.strip())
        lines.append("```")
        lines.append("")

        lines.append("### Candidate A Generated Email")
        lines.append("```text")
        lines.append(case_a.generated_email.strip())
        lines.append("```")
        lines.append("")

        lines.append("### Candidate B Generated Email")
        lines.append("```text")
        lines.append(case_b.generated_email.strip())
        lines.append("```")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def main() -> None:
    settings = load_settings()

    # Model/strategy A
    summary_a = evaluate(
        strategy="baseline",
        generation_model=settings.gen_model_a,
        judge_model=settings.judge_model,
    )
    save_outputs(summary_a, Path("outputs"))

    # Model/strategy B
    summary_b = evaluate(
        strategy="fewshot",
        generation_model=settings.gen_model_b,
        judge_model=settings.judge_model,
    )
    save_outputs(summary_b, Path("outputs"))

    rows = [
        {
            "label": "Candidate A",
            "strategy": summary_a.strategy,
            "generation_model": summary_a.generation_model,
            "judge_model": summary_a.judge_model,
            "fact_coverage_score": summary_a.average_scores["fact_coverage_score"],
            "tone_alignment_score": summary_a.average_scores["tone_alignment_score"],
            "professional_quality_score": summary_a.average_scores["professional_quality_score"],
            "overall_score": summary_a.average_scores["overall_score"],
        },
        {
            "label": "Candidate B",
            "strategy": summary_b.strategy,
            "generation_model": summary_b.generation_model,
            "judge_model": summary_b.judge_model,
            "fact_coverage_score": summary_b.average_scores["fact_coverage_score"],
            "tone_alignment_score": summary_b.average_scores["tone_alignment_score"],
            "professional_quality_score": summary_b.average_scores["professional_quality_score"],
            "overall_score": summary_b.average_scores["overall_score"],
        },
    ]

    compare_csv = Path("outputs") / "comparison_summary.csv"
    pd.DataFrame(rows).to_csv(compare_csv, index=False)

    compare_json = Path("outputs") / "comparison_summary.json"
    compare_json.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    analysis_path = build_analysis_text(rows, Path("reports") / "comparative_analysis.md")
    emails_path = build_generated_emails_text(
        summary_a, summary_b, Path("reports") / "generated_emails.md"
    )

    print("Comparison complete")
    print(f"Summary CSV : {compare_csv}")
    print(f"Summary JSON: {compare_json}")
    print(f"Analysis    : {analysis_path}")
    print(f"Emails      : {emails_path}")


if __name__ == "__main__":
    main()
