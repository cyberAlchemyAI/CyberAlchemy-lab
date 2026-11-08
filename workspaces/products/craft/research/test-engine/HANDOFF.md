# Handoff: Spec→Test Engine (DomainSpec v2)

Status: ready for research-tower seeding (not executed)
Date: 2026-06-12
Owner surface: DomainSpec v2
Authored by: `invoke` (mode: handoff)
Handoff type: `new-lifecycle-thread`
Source session: domainspec → arcanum integration review (2026-06-12)

## New-session prompt

> Build the **spec→test engine** as a DomainSpec v2 research tower: the asset that
> turns a feature's spec documents into an executable, coverage-checkable test
> suite. v1 specifies the *rules* for this mapping but never built the engine that
> runs them. Decide, under the Two-Lane Discipline, whether the engine is a pure
> deterministic rule executor or an LLM-assisted derivation — and prove or reject
> the chosen approach on one feature before any v1 mutation.

## Route rationale

This is a `new-lifecycle-thread` handoff, not an execution-continuation: the test
engine emerged as a to-be-built asset during the integration review, but it has no
design or work-pack yet. The next lifecycle should **start at a research-tower
SEED** (v2's equivalent of `invoke define`), not at `task-session`. Per the
DomainSpec v2 README, no template/validator/runtime change happens without a later
approved `task-session`, so this handoff opens research, not implementation.

## Context Builder selection summary

Selected from the source session only the facts an implementer needs to start the
test-engine tower well. Conversational history about the broader wedge/moat
migration was excluded (see below).

### Obligation coverage matrix

| # | Obligation (from prompt + handoff type) | Coverage | Evidence |
| - | --------------------------------------- | -------- | -------- |
| O1 | What exists today as the engine baseline | covered | `implementation/domainspec/TEST-PIPELINE.md` — deterministic doc→test rule tables (each transition-table row = 1 test case; fixed templates per doc section). |
| O2 | What does **not** exist | covered | No LLM-driven derivation engine anywhere in v1. Grep of all `.ts` for `anthropic\|openai\|claude\|llm\|generateText\|callModel` → zero hits. |
| O3 | Adjacent deterministic tooling to reuse | covered | `tools/validate-*.ts` (validators), `governance/tags/tools/` (code-tag extraction), `tools/generate-registry.ts`. |
| O4 | Open-core boundary placement | covered | The test-engine *method* is **free wedge** → public-arcanum eligible. Only a Lean formal-proof lever would be moat. A deterministic engine is wedge, not moat. |
| O5 | Constraints on where work may land | covered | Research writes stay under `projects/domainspec-v2/research/`; no v1 mutation without an approved `task-session`; submodule discipline applies. |
| O6 | Correctness coupling | flagged-gap | The `dcb-correctness` tower's read-set / freshness discipline likely constrains what "a test claim is still valid" means. Cross-tower seam, not yet resolved. |

## Selected session context

- **The engine is the gap, not the rules.** v1's `TEST-PIPELINE.md` is a complete,
  *deterministic* specification of how each DFDS doc section (`states.md`,
  `operations.md`, `interfaces.md`, `events.md`, `queries.md`, `workflows.md`,
  `mappings.md`) maps to specific test types. What is missing is the executor that
  consumes a spec and emits the tests. The "LLM-driven engine" described in the
  prior integration research **does not exist** — the only model in the loop today
  is an agent reading `TEST-PIPELINE.md` and writing tests by hand.
- **Determinism is the default hypothesis.** Because the mapping is already a rule
  table, Lane Z should build a pure deterministic executor. Lane A should hold the
  problem fixed ("turn a spec into a complete, coverage-checkable suite") and try a
  genuinely different solution (e.g. LLM-assisted generation behind a deterministic
  coverage gate, or property-based generation from typed nodes).
- **Boundary is clean.** A deterministic spec→test engine is the *commodity wedge*;
  it carries no moat material, so it is publishable into public arcanum later. Keep
  any Lean formal-proof / attestation lever out of this tower — that is a separate
  `g05`-blocked moat asset.

## Excluded context (tempting but not needed to start)

- The Craft schema/automation seam decision and the full wedge-vs-moat migration
  plan — relevant to *publishing* the engine, not to *building* it.
- The deleted `domainspec-arcanum-superset` feature pack and the
  `domainspec-into-arcanum-research` dispatch — integration-program history.
- The spec-ontology-unification tower's "node→code-pattern / edge→composition"
  model — adjacent and possibly synergistic, but a separate hypothesis.

## Target lifecycle / project boundary

- Artifact home: `projects/domainspec-v2/research/test-engine/`.
- Evidence source (read-only): `implementation/domainspec/TEST-PIPELINE.md` and the
  deterministic tooling under `tools/` and `governance/tags/tools/`.
- Runs under the [Two-Lane Discipline](../TWO-LANE-DISCIPLINE.md); nothing produced
  here is canonical until a later governed decision promotes it.

## Gaps and blockers

- **G1 (open):** the spec→code/test mapping seam overlaps the
  [`spec-ontology-unification`](../spec-ontology-unification/SEED.md) tower (edge →
  composition). Decide whether the test engine consumes that tower's typed graph or
  stays on today's doc-section model.
- **G2 (open):** correctness coupling with [`dcb-correctness`](../dcb-correctness/HANDOFF.md)
  — does a generated test carry a read-set so it can be invalidated when its source
  spec changes? Resolve before claiming "coverage-checkable."
- **G3 (open):** Lane A alternative is unfilled — name at least one genuinely
  different engine design before committing to the deterministic executor.

## Next-session start prompt

> Open the `test-engine` research tower. Lane Z: design a deterministic engine that
> executes `TEST-PIPELINE.md`'s rules to generate a test suite from one feature's
> spec, with explicit coverage accounting. Lane A: hold the problem fixed and
> propose one genuinely different derivation (LLM-assisted-behind-a-gate, or
> property-based-from-typed-nodes). Ground every claim in v1 evidence; mutate
> nothing in `implementation/domainspec`. Record receipts in `LANE-RECEIPTS.md`.

## Next route

`research-tower` (seed the `test-engine` tower) — or `invoke define` if a formal
define/glossary is wanted before the tower runs. Register the tower in the
DomainSpec v2 README tower table and the
`domainspec-v2-research-towers.dispatch.json` route once seeded.

## Provenance and output paths

- Observed capability: `invoke`
- Mode: `handoff`
- Target artifact: `test-engine` research tower (owner: DomainSpec v2)
- Output: `projects/domainspec-v2/research/test-engine/HANDOFF.md`
- Source session reference: domainspec → arcanum integration review, 2026-06-12
