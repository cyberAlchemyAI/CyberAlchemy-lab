# DCB-for-Correctness — shareable pack

A self-contained write-up of what we found about using Dynamic Consistency
Boundaries for correctness, written for a reader who **knows DCB but not
DomainSpec**.

## What to send

Two versions of the same finding:

- **Victor's voice (recommended for sending)** — opens on a real case, grounds
  "freshness" before naming it, less polished.
  - [DCB-FOR-CORRECTNESS.victor.md](DCB-FOR-CORRECTNESS.victor.md)
  - [DCB-FOR-CORRECTNESS.victor.pdf](DCB-FOR-CORRECTNESS.victor.pdf)
- **Polished reference version** — denser, more formal.
  - [DCB-FOR-CORRECTNESS.md](DCB-FOR-CORRECTNESS.md)
  - [DCB-FOR-CORRECTNESS.pdf](DCB-FOR-CORRECTNESS.pdf)

Either one stands alone. No DomainSpec knowledge required.

## How the PDFs are built

Rebuilt with the global `pdfkit` chrome engine (markdown → themed HTML →
headless-Chromium print), e.g.:

```bash
python3 ~/.claude/tools/pdfkit/pdfkit.py build DCB-FOR-CORRECTNESS.victor.md \
  --out DCB-FOR-CORRECTNESS.victor.pdf \
  --subtitle "When DCB actually helps — and when it's overkill" \
  --author "DomainSpec v2 research" --date "2026-06-22" \
  --accent "#2b6cb0" --accent2 "#dd6b20"
```

## Voice preset

- [whisper-preset.md](whisper-preset.md) — the Whisper preset
  (`domainspec_v2_research_finding_victor`) used to write the Victor-voice draft.

## Internal provenance (not for the external reader)

The pack distills two research towers and one executed toy:

- `../dcb-correctness/` — the correctness tower (SYNTHESIS, RESEARCH-STRATEGY,
  LANE-A-ALTERNATIVES, TOY-SCENARIO, HANDOFF).
- `../dcb-saga-correctness/` — the saga tower and the bounded TypeScript witness
  (SYNTHESIS, TOY-SAGA-SCENARIO, `toy-run-result.md` / `.json`, `toy-harness/`).

If you change a finding in a source tower, re-derive the pack rather than editing
the distilled claims in place.
