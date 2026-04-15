# AI Engineer Assessment - Email Generation Assistant (Groq)

This project implements a complete assessment submission for the Email Generation Assistant task using Groq LLMs and Python.

## What this includes

- Email generator from 3 inputs: `intent`, `key_facts`, `tone`
- Advanced prompt engineering with two strategies:
  - `baseline` (role + strict constraints)
  - `fewshot` (role + in-context example)
- 10 test scenarios with human reference emails (`data/scenarios.json`)
- 3 custom evaluation metrics (task-specific)
- Automated evaluation pipeline with CSV/JSON output
- Model/strategy comparison pipeline + analysis summary

## Tech stack

- Python 3.11+
- Groq Python SDK
- pydantic
- pandas
- rapidfuzz
- python-dotenv
- pytest

## Project structure

```text
.
+-- data/
¦   +-- scenarios.json
+-- outputs/
+-- deliverables/
¦   +-- model_a_results.csv
¦   +-- model_a_results.json
¦   +-- model_b_results.csv
¦   +-- model_b_results.json
¦   +-- comparison_summary.csv
¦   +-- comparison_summary.json
+-- reports/
¦   +-- comparative_analysis.md
¦   +-- generated_emails.md
¦   +-- final_report.md
+-- src/
¦   +-- compare_models.py
¦   +-- config.py
¦   +-- data_loader.py
¦   +-- evaluate.py
¦   +-- groq_service.py
¦   +-- metrics.py
¦   +-- prompts.py
¦   +-- schemas.py
+-- tests/
¦   +-- test_metrics.py
+-- .env.example
+-- requirements.txt
+-- README.md
```

## Setup

1. Create and activate virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Create `.env` from example and add your key.

```powershell
Copy-Item .env.example .env
```

Set:

- `GROQ_API_KEY`
- Optional model overrides:
  - `GEN_MODEL_A`
  - `GEN_MODEL_B`
  - `JUDGE_MODEL`

## Run evaluation for one strategy

```powershell
python -m src.evaluate --strategy baseline --model llama-3.1-8b-instant --judge-model llama-3.1-8b-instant
```

or

```powershell
python -m src.evaluate --strategy fewshot --model llama-3.3-70b-versatile --judge-model llama-3.1-8b-instant
```

This generates:

- `outputs/<strategy>_<model>_<timestamp>.json`
- `outputs/<strategy>_<model>_<timestamp>.csv`

## Run full model/strategy comparison

```powershell
python -m src.compare_models
```

This runs both candidates using `.env` settings and writes:

- `outputs/comparison_summary.csv`
- `outputs/comparison_summary.json`
- `reports/comparative_analysis.md`
- `reports/generated_emails.md` (all generated emails for both candidates + references)

## Tracked raw data for submission

Since `outputs/*.csv` and `outputs/*.json` are gitignored, copy latest run artifacts into `deliverables/` before pushing:

```powershell
python -m src.compare_models
```

Then ensure these files exist (already prepared in this repo):

- `deliverables/model_a_results.csv`
- `deliverables/model_a_results.json`
- `deliverables/model_b_results.csv`
- `deliverables/model_b_results.json`
- `deliverables/comparison_summary.csv`
- `deliverables/comparison_summary.json`

## Quick test before deploy

Run this exact sequence:

```powershell
python -m pytest -q
python -m src.compare_models
Get-Content outputs\comparison_summary.csv
Get-Content reports\comparative_analysis.md
Get-Content reports\generated_emails.md -TotalCount 80
```

Expected:

- `pytest` passes
- comparison files are regenerated in `outputs/`
- analysis and generated-emails files are regenerated in `reports/`
- `comparison_summary.csv` shows two rows: `Candidate A` and `Candidate B`

## Custom metrics

1. `fact_coverage_score` (0-1)
- Deterministic metric.
- Checks how many required facts are present in generated email using fuzzy string match + token overlap.

2. `tone_alignment_score` (0-1)
- LLM-as-a-judge metric.
- Scores whether style matches requested tone: formal, casual, urgent, empathetic.

3. `professional_quality_score` (0-1)
- Hybrid metric.
- `0.4 * deterministic_format_score + 0.6 * llm_quality_score`
- Deterministic checks include subject line, structure, sign-off, and word-length bounds.

## Prompting technique used

Advanced prompting includes:

- Explicit role assignment
- Hard output constraints (mandatory facts + structure)
- Few-shot in-context example (for strategy B)

## Tests

```powershell
pytest -q
```

## Notes

- This repository is intentionally assessment-focused and reproducible.
- Human reference emails are in the dataset for qualitative comparison and report completeness.
- Submission repo: `https://github.com/raj-abhit/Email-assistant`
