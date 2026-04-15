from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from .config import load_settings
from .data_loader import load_scenarios
from .groq_service import GroqService
from .metrics import combine_quality_scores, fact_coverage_score, format_quality_score
from .prompts import METRIC_DEFINITIONS, build_generation_messages, build_judge_messages
from .schemas import EvaluatedCase, RunSummary


def evaluate(strategy: str, generation_model: str, judge_model: str) -> RunSummary:
    settings = load_settings()
    service = GroqService(settings.groq_api_key)

    scenarios = load_scenarios()
    evaluated_cases: list[EvaluatedCase] = []

    for scenario in scenarios:
        gen_messages = build_generation_messages(scenario, strategy=strategy)  # type: ignore[arg-type]
        generated_email = service.chat(
            model=generation_model,
            messages=gen_messages,
            temperature=settings.temperature,
        ).strip()

        judge_messages = build_judge_messages(
            intent=scenario.intent,
            tone=scenario.tone,
            key_facts=scenario.key_facts,
            generated_email=generated_email,
        )
        judge = service.judge(model=judge_model, messages=judge_messages)

        fact_score = fact_coverage_score(scenario.key_facts, generated_email)
        deterministic_quality = format_quality_score(generated_email)
        quality_score = combine_quality_scores(deterministic_quality, judge.professional_quality_score)

        overall = round((fact_score + judge.tone_alignment_score + quality_score) / 3, 4)

        evaluated_cases.append(
            EvaluatedCase(
                scenario_id=scenario.id,
                strategy=strategy,
                generation_model=generation_model,
                judge_model=judge_model,
                fact_coverage_score=fact_score,
                tone_alignment_score=round(judge.tone_alignment_score, 4),
                professional_quality_score=quality_score,
                overall_score=overall,
                generated_email=generated_email,
                tone_feedback=judge.tone_feedback,
                quality_feedback=judge.quality_feedback,
            )
        )

    avg_fact = round(sum(c.fact_coverage_score for c in evaluated_cases) / len(evaluated_cases), 4)
    avg_tone = round(sum(c.tone_alignment_score for c in evaluated_cases) / len(evaluated_cases), 4)
    avg_quality = round(sum(c.professional_quality_score for c in evaluated_cases) / len(evaluated_cases), 4)
    avg_overall = round(sum(c.overall_score for c in evaluated_cases) / len(evaluated_cases), 4)

    return RunSummary(
        strategy=strategy,
        generation_model=generation_model,
        judge_model=judge_model,
        metric_definitions=METRIC_DEFINITIONS,
        average_scores={
            "fact_coverage_score": avg_fact,
            "tone_alignment_score": avg_tone,
            "professional_quality_score": avg_quality,
            "overall_score": avg_overall,
        },
        cases=evaluated_cases,
    )


def save_outputs(summary: RunSummary, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = f"{summary.strategy}_{summary.generation_model.replace('/', '_')}_{timestamp}"

    json_path = output_dir / f"{prefix}.json"
    csv_path = output_dir / f"{prefix}.csv"

    json_payload = {
        "strategy": summary.strategy,
        "generation_model": summary.generation_model,
        "judge_model": summary.judge_model,
        "metric_definitions": summary.metric_definitions,
        "average_scores": summary.average_scores,
        "cases": [case.model_dump() for case in summary.cases],
    }
    json_path.write_text(json.dumps(json_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    df = pd.DataFrame([case.model_dump() for case in summary.cases])
    df.to_csv(csv_path, index=False)

    return json_path, csv_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Email Assistant evaluation for one strategy/model.")
    parser.add_argument("--strategy", choices=["baseline", "fewshot"], required=True)
    parser.add_argument("--model", required=True, help="Groq generation model id")
    parser.add_argument("--judge-model", required=True, help="Groq judge model id")
    parser.add_argument("--output-dir", default="outputs", help="Directory for csv/json outputs")
    args = parser.parse_args()

    summary = evaluate(strategy=args.strategy, generation_model=args.model, judge_model=args.judge_model)
    json_path, csv_path = save_outputs(summary, Path(args.output_dir))

    print("Evaluation complete")
    print(f"JSON: {json_path}")
    print(f"CSV : {csv_path}")
    print("Average scores:")
    for key, value in summary.average_scores.items():
        print(f"  - {key}: {value}")


if __name__ == "__main__":
    main()
