# TASK-FMT-VERIFY: Readiness Closeout

Layer: L3
Status: completed-with-residue

## Objective

Verify that the formal-modeling surface is honest, navigable, and synchronized back into the tower.

## Source Contracts

- All task receipts.
- `../../../gates/closure-gates.md`
- `../../../LEARNING-PACK.md`
- `../../PLAN-TRANSPORT.md`

## Smallest Working Unit Exemption

This is a closure-only task and uses a `VERIFY` exemption. It has one closeout SWU for traceability.

### SWU-FMT-008

- Goal: Close readiness and sync tower status.
- Dependencies: SWU-FMT-001 through SWU-FMT-007.
- Write scope: `../../../gates/closure-gates.md`, `../../../LEARNING-PACK.md`, `invoke-plan/PLAN-TRANSPORT.md`, final receipts.
- Done criteria: tower gate status matches actual tool/model validation results.
- Acceptance evidence: markdown link checks, scoped git status, no tracked binaries, receipt inventory.
- Validation surface:
  - `bash tools/check_markdown_links.sh projects/domainspec-v2/research/alloy-tla-modeling/README.md`
  - `find projects/domainspec-v2/research/alloy-tla-modeling -name '*.md' ... check links`
  - `git status --short projects/domainspec-v2/research/alloy-tla-modeling .formal-tools`
- Execution owner: local-fallback.
- Handoff note: Do not promote the tower to canonical validator readiness unless model runs actually pass.
- Status: completed-with-residue 2026-06-16.
- Evidence:
  - `../../run-results/swu-fmt-008-readiness-closeout.md`
  - `../../../gates/closure-gates.md`
  - `../../../LEARNING-PACK.md`
  - `../../PLAN-TRANSPORT.md`
- Validation result: pass-with-residue. Markdown links resolve and `.formal-tools/` remains untracked; TLA+ freshness counterexample remains the main model residue.
