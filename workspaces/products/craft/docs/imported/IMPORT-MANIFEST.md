---
title: DomainSpec v1 → v2 Import Manifest
status: active (migration in progress)
provenance_v1_commit: 33859b561dc34e3d0b9cb3da76b6cb3d196daa65
source_of_verdicts: research/2026-06-29-v1-import-triage/findings.md
boundary: impl/test-derivation-engine/src/rules IS THE MOAT — private, NEVER publish to public arcanum/
---

# v1 → v2 Import Manifest ("the way")

The auditable ledger for migrating DomainSpec from **v1** (`implementation/domainspec/`,
becoming a FROZEN evidence source) into **v2** (`projects/domainspec-v2/`, the implementation
home). Every row: v1 source → v2 dest · verdict · status · batch. Verdicts come from the import
triage ([findings.md](research/2026-06-29-v1-import-triage/findings.md): **3 IMPORT / 25
REFORMULATE / 4 DROP**).

## Legend
- **verdict** — `IMPORT` (copy verbatim: genuine net-new or reused as-is) · `REFORMULATE` (copy to unblock the build, then re-author for v2's *govern+enforce Ontology A on evidence* mandate) · `DROP` (never import).
- **status** — `pending` · `imported-verbatim` · `reformulation-pending` · `reformulated` · `dropped`.
- **boundary** — `private-moat` = stays private, never published.

## Batch 1 — engine core (makes v2 buildable) — FORKED ✅ · build-proof: see RESULT below

| v1 source | v2 dest | verdict | status | boundary | triage row |
|---|---|---|---|---|---|
| `tools/test-derivation-engine/` | `impl/test-derivation-engine/` | IMPORT | imported-verbatim | `src/rules` = private-moat | 1,2 (executor + obligation_key) |
| `TAXONOMY.md` | `impl/spec/TAXONOMY.md` | REFORMULATE | reformulation-pending | — | 23 |
| `RELATIONSHIPS.md` | root `definitions/relationships/relationships.yml` (v2 projection deleted) | REFORMULATE | reformulated (R3A + R0; consumed from root) | — | 24 |
| `AXIOMS.md` | `authority/AXIOMS.md` + `authority/AXIOMS.yml` (`impl/spec` projection deleted) | REFORMULATE | reformulated (R1 closeout + definition-sync) | — | 28 |
| `DRIFT-CONVERGENCE.md` | `impl/spec/DRIFT-CONVERGENCE.md` | REFORMULATE | reformulation-pending | — | 15 |
| `TEST-PIPELINE.md` | `impl/spec/TEST-PIPELINE.md` | REFORMULATE | reformulation-pending | — | 4 |
| `CONSTITUTION.md` | `impl/spec/CONSTITUTION.md` | REFORMULATE | reformulation-pending | — | (C1–C11, gov. by AXIOMS) |

## Batch 2 — validators + drift cluster — TOOLING IMPORTED 2026-06-29; reformulation-pending

| v1 source | v2 dest | verdict | status | triage row |
|---|---|---|---|---|
| `tools/validate-relationships.ts` | `impl/tools/validate-relationships.ts` | REFORMULATE | imported-verbatim (reformulation-pending) | 24 |
| `tools/validate-doc-links.ts` | `impl/tools/validate-doc-links.ts` | REFORMULATE | imported-verbatim (reformulation-pending) | C9 / A1 validator |
| `governance/tags/tools/` + schema/docs (CODE-TAG-SCHEMA, WAIVERS, COMPOSABILITY-PATTERNS, REMEDIATION, README, examples) | `impl/governance/tags/` | REFORMULATE | imported-verbatim (reformulation-pending) | 10–16 |
| `governance/tags/CODE-TAG-DRIFT-REPORT-*.md` + `code-tags*.json` (v1 DATA) | — | DROP (data, not tooling) | left in v1 | — |

**Reformulation-pending for Batch 2 (the REFORMULATE work still owed):**
- the validators assume `docs/features/` + a repo-root `RELATIONSHIPS.md` — retarget to v2's spec surface (`impl/spec/RELATIONSHIPS.md`, v2 feature packs) and wire a tsx runtime so **C9/C10/C11 become runnable, not just declared**;
- `code-tag-waivers.yaml` carries v1 waiver entries — reset to empty for v2;
- the code-tag tooling is **drift governance**'s methods (its enforcement is drift, not validation) — bind accordingly.

## Batch 3 — audit + layering — pending (reformulate)

| v1 source | v2 dest | verdict | status | triage row |
|---|---|---|---|---|
| `.claude/skills/domainspec-audit-alignment` | v2 skill | REFORMULATE | pending | 18 |
| `.claude/skills/domainspec-audit-layering` | v2 skill | REFORMULATE | pending | 25,26 |
| `ADLC-ALIGNMENT.md` | `impl/spec/` | REFORMULATE | pending | 27 |
| Lean audit *method* (VLACHOPULOS/SMITHE) | v2 harness | REFORMULATE | pending | 19 (method only, not physics content) |

## Batch 4 — backend pattern-card evidence staging — triaged 2026-07-12

No legacy card was copied into authority. Each destination points to the
non-authoritative [backend-card staging matrix](development/architecture-pattern-enforcement/cards/backend/README.md),
which scopes reusable evidence and records unsafe residue. Triage states govern
staging readiness; manifest verdict/status retain the import vocabulary above.

| v1 source | v2 dest | verdict | status | batch | triage state |
|---|---|---|---|---|---|
| `architecture/pattern-library/concepts/backend/entity.md` @ `33859b561dc34e3d0b9cb3da76b6cb3d196daa65` | backend-card staging matrix | REFORMULATE | reformulation-pending | 4 | `evidence-ready` |
| `architecture/pattern-library/concepts/backend/value-object.md` @ `33859b561dc34e3d0b9cb3da76b6cb3d196daa65` | backend-card staging matrix | REFORMULATE | pending | 4 | `staged-review` |
| `architecture/pattern-library/concepts/backend/enum-type.md` @ `33859b561dc34e3d0b9cb3da76b6cb3d196daa65` | backend-card staging matrix | REFORMULATE | pending | 4 | `staged-review` |
| `architecture/pattern-library/concepts/backend/operation.md` @ `33859b561dc34e3d0b9cb3da76b6cb3d196daa65` | backend-card staging matrix | REFORMULATE | pending | 4 | `staged-review` |
| `architecture/pattern-library/concepts/backend/query.md` @ `33859b561dc34e3d0b9cb3da76b6cb3d196daa65` | backend-card staging matrix | REFORMULATE | reformulation-pending | 4 | `evidence-ready` |
| `architecture/pattern-library/concepts/backend/calculation.md` @ `33859b561dc34e3d0b9cb3da76b6cb3d196daa65` | backend-card staging matrix | REFORMULATE | reformulation-pending | 4 | `evidence-ready` |
| `architecture/pattern-library/concepts/backend/rule.md` @ `33859b561dc34e3d0b9cb3da76b6cb3d196daa65` | backend-card staging matrix | REFORMULATE | pending | 4 | `staged-review` |
| `architecture/pattern-library/concepts/backend/policy.md` @ `33859b561dc34e3d0b9cb3da76b6cb3d196daa65` | backend-card staging matrix | REFORMULATE | pending | 4 | `staged-review` |
| `architecture/pattern-library/concepts/backend/workflow.md` @ `33859b561dc34e3d0b9cb3da76b6cb3d196daa65` | backend-card staging matrix | REFORMULATE | pending | 4 | `staged-review` |
| `architecture/pattern-library/concepts/backend/saga.md` @ `33859b561dc34e3d0b9cb3da76b6cb3d196daa65` | backend-card staging matrix (residue only) | DROP | dropped | 4 | `reject-or-superseded` |
| `architecture/pattern-library/concepts/backend/interface.md` @ `33859b561dc34e3d0b9cb3da76b6cb3d196daa65` | backend-card staging matrix | REFORMULATE | reformulation-pending | 4 | `evidence-ready` |
| `architecture/pattern-library/concepts/backend/event.md` @ `33859b561dc34e3d0b9cb3da76b6cb3d196daa65` | backend-card staging matrix | REFORMULATE | reformulation-pending | 4 | `evidence-ready` |
| `architecture/pattern-library/concepts/backend/mapping.md` @ `33859b561dc34e3d0b9cb3da76b6cb3d196daa65` | backend-card staging matrix | REFORMULATE | pending | 4 | `staged-review` |
| `architecture/pattern-library/concepts/backend/state-machine.md` @ `33859b561dc34e3d0b9cb3da76b6cb3d196daa65` | backend-card staging matrix | REFORMULATE | pending | 4 | `staged-review` |

## DROP — never imported

| v1 capability | verdict | triage row |
|---|---|---|
| LLM-mediated test generator | DROP | 8 (superseded downgrade) |
| `domainspec-pipeline` orchestrator | DROP | 9 (app-builder, adapter line) |
| promotion-status auto-writer | DROP | 17 (write-authority proviso) |
| app-runtime concerns (CQRS / auth / RLS / agent-state) | DROP | 31 (below adapter line) |

## Genuine net-new IMPORTs (carried, or still to build)
- Spec→test **executor** (row 1) + `obligation_key` seam (row 2) — present in the engine fork.
- DCB concurrency/TOCTOU edge (row 3) — net-new for everyone; **not built yet** (tracked in the `dcb-correctness` tower), not in this fork.
- **`impl/spec/DEFINITIONS.md` (DS-D1 meta-types + DS-D2 edge verbs)** — **net-new; the 6-doc Batch-1 set omitted a domain-vocabulary home** (v1 kept definitions under `research/.../definitions/`). Built by reformulation **R7** (aggregates R2 TAXONOMY + R3 RELATIONSHIPS); owner `definitions-governance`. Distinct from the governance/synthesis vocabulary in `definitions/DEFINITIONS.md` (`domainspec-v2-D3/D4/D5`, consolidated 2026-07-01).

## Freeze gate
`implementation/domainspec/` becomes a FROZEN evidence source once v2 is self-contained — all
REFORMULATE rows reformulated AND the build-proof green. Until then v1 stays readable, not edited.
