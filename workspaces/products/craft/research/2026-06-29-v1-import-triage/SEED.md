---
node_type: research
subject: DomainSpec v1 → v2 import triage
dispatch_id: 2026-06-29-domainspec-v1-import-triage
dispatch_type: research
discipline: claim <= proof; one verdict per capability; found owner = build-from-owned, never a kill
date: 2026-06-29
---

# SEED — DomainSpec v1 → v2 import triage

Shared context for all dispatch agents. Read this first; your `initial_prompt` adds
your area + role on top of it.

## Goal

DomainSpec **v2 = govern + enforce Ontology A (the DomainSpec language) on evidence**
(owned: `.arcanum/inventory/entries/ontology-operationalization-in-the-machine-synthesis.md`).
This is **build-from-owned** over v1, **not** a greenfield rebuild. Produce a v1→v2 import
triage: per capability, exactly one verdict.

## Verdict vocabulary (one per capability)

- **IMPORT** (ASSIMILATE-NOW) — bring it into v2; may need net-new wiring.
- **REFORMULATE** (BUILD-FROM-OWNED) — an owner exists; re-author/sharpen into v2, do not re-import. *A found owner is this, never a kill.*
- **DROP** (SKIP) — out-of-layer / overshoot / a downgrade.

## Build on these owned sweeps — do NOT re-derive them

- `research/2026-06-29-external-assimilation-allium-grain-glyph/ASSIMILATION-TABLE.md` — v1 owners + worked verdicts (esp. S3 engine=moat, B1 code→spec writeback).
- `research/2026-06-29-correctness-ownership-sweep/findings.md` — audit/correctness owned-vs-net-new map.
- `research/test-engine/HANDOFF.md` — the engine offer (note: calls the deterministic engine the FREE wedge — contested below).

## The contradiction the `offers` pair must resolve

`test-engine/HANDOFF.md` calls the **deterministic engine the FREE wedge** (publishable); ASSIMILATION-TABLE S3 + memory call it the **proprietary moat**. Resolve which is free, which is moat, and where the boundary sits (moat = attestation + governance-data + vertical per the inventory; provability = amplifier).

## v1 evidence (READ-ONLY — no v1 mutation)

`implementation/domainspec/` (skills under `.claude/skills/`, docs, `tools/test-derivation-engine/`) + `domainspec-lean-formalization/`.

## Guardrails (every row carries them)

claim ≤ proof · two-ontologies (language A vs cav2 authority B — align, not merge) · the write-authority proviso (no modeling surface writes promotion-status) · the adapter line (no app-runtime imports) · the free/moat boundary.

## Output contract

Each agent writes its memo to `<this folder>/<area>-<role>.md` and returns ONLY a short summary (not the full memo). The synthesizer (Spivak) writes `findings.md` — the triage table — citing the memos.
