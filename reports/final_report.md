# Final Report - AI Engineer Candidate Assessment: Email Generation Assistant

## Submission Info
- Candidate Name: `Abhit Raj`
- Date: `2026-04-15`
- GitHub Repository: `https://github.com/raj-abhit/Email-assistant`

## 1. Prompt Template Used

### Strategy A - Baseline (Role + Constraint Prompting)
System prompt:

```text
You are a senior executive communications assistant. Write polished, professional emails with clear structure and concise language. Return only the email text.
```

User template:

```text
Write an email using the details below.

Intent: {intent}
Tone: {tone}
Mandatory facts:
- {fact_1}
- {fact_2}
- ...

Rules:
1) Include every mandatory fact exactly once in natural wording.
2) Include a clear subject line.
3) Keep length between 120 and 220 words.
4) Use a greeting and sign-off.
```

### Strategy B - Few-Shot (Role + In-Context Example)
System prompt:

```text
You are an enterprise email writing specialist. Follow the examples and constraints exactly, then produce one final email only.
```

Few-shot example input:

```text
Intent: Confirm interview schedule
Tone: formal
Mandatory facts:
- Interview is on May 7 at 2:00 PM
- Format is virtual via Zoom
- Panel includes Product Lead and Engineering Manager
- Ask candidate to confirm availability
```

Few-shot example output:

```text
Subject: Interview Schedule Confirmation - May 7 at 2:00 PM

Dear Candidate,

Thank you for progressing to the next stage of our process. Your interview is scheduled for May 7 at 2:00 PM and will be conducted virtually via Zoom.

The interview panel will include our Product Lead and Engineering Manager. Please confirm your availability for this slot at your earliest convenience.

We look forward to speaking with you.

Best regards,
Hiring Team
```

Final user template:

```text
Now write the final email for this input.

Intent: {intent}
Tone: {tone}
Mandatory facts:
- {fact_1}
- {fact_2}
- ...

Constraints:
- Include all mandatory facts.
- Match requested tone.
- Use subject, greeting, body, and sign-off.
- Keep it concise and professional.
Return only the final email.
```

## 2. Custom Metric Definitions and Logic

### Metric 1: Fact Coverage Score
- Purpose: Verify factual completeness of generated email.
- Type: Deterministic automated metric.
- Logic: For each required fact, compute fuzzy partial ratio and token overlap against generated email text. A fact is marked covered if similarity crosses threshold.
- Formula: `covered_facts / total_required_facts`
- Score range: `0.0 to 1.0`

### Metric 2: Tone Alignment Score
- Purpose: Verify alignment with requested tone (`formal`, `casual`, `urgent`, `empathetic`).
- Type: LLM-as-a-judge.
- Logic: A judge model evaluates style/tone fidelity and returns numeric score.
- Score range: `0.0 to 1.0`

### Metric 3: Professional Quality Score
- Purpose: Measure clarity, structure, grammatical quality, and concise business style.
- Type: Hybrid metric.
- Logic:
  - Deterministic format checks: subject line presence, structural paragraphing, length bounds, sign-off presence.
  - LLM quality judgment: clarity, grammar, structure, conciseness.
  - Combined score formula: `0.4 * format_score + 0.6 * llm_quality_score`
- Score range: `0.0 to 1.0`

## 3. Raw Evaluation Data

Generated artifacts:
- `outputs/baseline_llama-3.1-8b-instant_20260415_140456.csv`
- `outputs/baseline_llama-3.1-8b-instant_20260415_140456.json`
- `outputs/fewshot_llama-3.3-70b-versatile_20260415_140539.csv`
- `outputs/fewshot_llama-3.3-70b-versatile_20260415_140539.json`
- `outputs/comparison_summary.csv`
- `outputs/comparison_summary.json`

## 4. Comparative Analysis (Section 3)

### 4.1 Which model/strategy performed better across the 3 custom metrics?
Using the same 10 scenarios and same metric pipeline for both candidates:

- Candidate A (`baseline`, `llama-3.1-8b-instant`)
  - Fact Coverage: `0.925`
  - Tone Alignment: `0.860`
  - Professional Quality: `0.970`
  - Overall: `0.9183`

- Candidate B (`fewshot`, `llama-3.3-70b-versatile`)
  - Fact Coverage: `0.925`
  - Tone Alignment: `0.870`
  - Professional Quality: `0.950`
  - Overall: `0.9150`

Result: **Candidate A performed better overall** (`0.9183` vs `0.9150`).

### 4.2 Biggest failure mode of the lower-performing candidate
The lower-performing candidate (Candidate B) showed its main weakness in **professional quality**, where it scored lower (`0.95`) than Candidate A (`0.97`). This reduced overall average despite slightly better tone alignment.

### 4.3 Production recommendation and justification
Recommended for production: **Candidate A (baseline + llama-3.1-8b-instant)**.

Justification:
- Highest overall average score (`0.9183`).
- Equal factual coverage (`0.925`) compared with Candidate B.
- Better professional quality (`0.97`), which is critical for business email reliability.
- Simpler prompting strategy (`baseline`) with strong output consistency.

## 5. Conclusion

This implementation satisfies the assessment requirements with a reproducible generation + evaluation pipeline, custom metrics, and model comparison. The strongest candidate was the baseline strategy on `llama-3.1-8b-instant`, primarily due to superior professional writing quality while maintaining high factual recall.

For production hardening, next improvements would include:
- Add scenario-level error taxonomy (missing fact, tone drift, formatting issue).
- Increase test set diversity beyond 10 cases.
- Add human spot-audit loop for periodic calibration of LLM-judge scoring.
