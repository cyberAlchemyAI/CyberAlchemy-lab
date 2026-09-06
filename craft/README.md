# DomainSpec v2

Status: **implementation home** (migrating from v1 by import+reformulate, 2026-06-29) — and still the research-tower program
Owner: DomainSpec v2
Started: 2026-06-11

Current execution runtime: Node `26.8.1` in the repository's pinned container;
see [`RUNTIME.json`](RUNTIME.json) and run [`validate-runtime.mjs`](validate-runtime.mjs)
through `toolchains/node-typescript/bin/node-env`. Historical receipts retain the
runtime they actually observed and do not control current execution. The current
container evidence is recorded in the
[`Node 26 migration receipt`](development/implementation-conformance/ontology-experiment/validation-receipts/2026-08-29-node-26-runtime-migration.json).

DomainSpec v2 is the next iteration of the DomainSpec discipline. **As of 2026-06-29, v2 is
becoming the implementation home:** v1 ([`implementation/domainspec`](../../implementation/domainspec))
is being **frozen as an evidence source**, and the necessary capabilities are being **imported and
reformulated** into v2 — see [`IMPORT-MANIFEST.md`](IMPORT-MANIFEST.md), driven by the
[v1→v2 import triage](research/2026-06-29-v1-import-triage/findings.md). The forked implementation
lives under [`impl/`](impl/). v2 also remains the research-tower program described below.

## Architecture and guide

- [Product Thesis](PRODUCT-THESIS.md) — the canonical statement of the problem,
  promise, product model, moat, boundaries, and success criterion.
- [DomainSpec v2 Architecture](ARCHITECTURE.md) — the integrated system map across
  authority, language, specification, compilation, derivation, conformance, evidence,
  EVF, and owner gates.
- [Complete Guide](COMPLETE-GUIDE.md) — the teaching-oriented walkthrough, examples,
  and practical usage reference.
- [Product Ontology](ontology/README.md) — the canonical private business/system graph
  and evidence-backed realization bridge.

## Implementation home (`impl/`) — migrated from v1

The forked implementation lives under [`impl/`](impl/):
- `impl/test-derivation-engine/` — the deterministic engine (fork of v1's; `src/rules/` is the **private moat** — never publish to public `arcanum/`).
- `impl/spec/` — remaining Ontology-A contract/import surfaces (TAXONOMY, DRIFT-CONVERGENCE, TEST-PIPELINE, CONSTITUTION) while reformulation proceeds; AXIOMS now lives at [`authority/AXIOMS.md`](authority/AXIOMS.md) + [`authority/AXIOMS.yml`](authority/AXIOMS.yml), and RELATIONSHIPS authority lives under root [`definitions/relationships/`](definitions/relationships/).

Migration is tracked in [`IMPORT-MANIFEST.md`](IMPORT-MANIFEST.md) (every v1→v2 row: verdict, status, batch). The 4 DROP-verdict v1 capabilities are never imported.

## How v2 works

v2 advances through **research towers** (see the
[`research-tower`](../../.claude/skills/research-tower/SKILL.md) skill). A tower
turns one hypothesis or source corpus into source-backed, auditable
understanding with explicit borrow / analogy / block / promotion-candidate
decisions. Nothing a tower produces is canonical until a later governed
decision promotes it.

Every tower runs under the [Two-Lane Discipline](research/TWO-LANE-DISCIPLINE.md):

- **Lane Z — zig-zag:** build the proposed idea out, alternating generation and
  critique until it either holds or breaks.
- **Lane A — alternatives:** hold the *underlying problem* fixed and propose a
  genuinely different solution, so we never ship the first idea by default.

## Active research towers

| Tower | Hypothesis under test | Underlying problem | Seed |
| --- | --- | --- | --- |
| [target-state](research/target-state/SEED.md) | Make "target state" an explicit, *buildable* artifact, borrowing from Narrative-Driven Development. | DomainSpec implies a target state everywhere but never formalizes it, so agents lack the discipline of "where are we going / what does done look like." | [SEED](research/target-state/SEED.md) |
| [spec-ontology-unification](research/spec-ontology-unification/SEED.md) | Treat spec and ontology as one typed graph (tree inside a feature, graph across features); feed specs to ephemeral implementation agents that only know node→code-pattern and edge→composition. | Spec→code mapping is implicit, so implementation agents are expensive and drift-prone; spec and code are really two forms of the same domain taxonomy. | [SEED](research/spec-ontology-unification/SEED.md) |
| [dcb-correctness](research/dcb-correctness/HANDOFF.md) | Dynamic Consistency Boundaries as a selective spec-to-code correctness discipline. | Existing validators check a snapshot, not whether a later claim was made against still-current facts. | (already underway) |
| [alloy-tla-modeling](research/alloy-tla-modeling/README.md) | Use Alloy for bounded graph-completeness counterexamples and TLA+/PlusCal for temporal cross-feature Workflow behavior, reusing the historical corpus and TypeScript bounded witness. | DomainSpec v2 needs formal-modeling lanes without overclaiming that TypeScript, DCB, Alloy, or TLA+ alone proves scoped-orchestration correctness. | [README](research/alloy-tla-modeling/README.md) |

> Moved out: the **intent-latitude tags** work (`[literal]`/`[goal]`/`[constraint]`
> grounded by a validator) was reclassified as an IDE chat-ergonomics primitive and
> now lives at
> [`projects/ide-ergonomics/intent-latitude-tags/`](../ide-ergonomics/intent-latitude-tags/README.md).
> The `target-state` and `spec-ontology-unification` towers above still cross-reference it.

## Route

The initial target-state and spec-ontology towers are sequenced and gated by one
validated dispatch:
[`domainspec-v2-research-towers.dispatch.json`](research/domainspec-v2-research-towers.dispatch.json).
That route is **designed and validated, not yet executed**. Later towers can
carry their own route or proposed subagent sheet inside their tower folder; for
example, `alloy-tla-modeling` records its `/domainspec-subagents-strategy`
proposal in
[`subagents/PROPOSED-DISPATCH.md`](research/alloy-tla-modeling/subagents/PROPOSED-DISPATCH.md).

## Artifact conventions

- Each tower owns a subfolder under `research/<tower>/` and keeps its own
  seed or `README.md`, `LANE-RECEIPTS.md` when lanes run, learning pack, and
  tower-local notes there.
- Cross-tower, program-level artifacts live at `research/` root and are prefixed
  `PROGRAM-` (e.g. `PROGRAM-SYNTHESIS.md`, `PROGRAM-HANDOFF.md`) so they never
  collide with a tower's own files.
- `dcb-correctness` predates the Two-Lane Discipline; it keeps its four concern
  lanes and carries a recorded alternatives-lane gap (see its
  [RESEARCH-STRATEGY.md](research/dcb-correctness/RESEARCH-STRATEGY.md)).

## Boundaries

- **v1 is frozen** (`implementation/domainspec/`) — a read-only evidence source; new work lands in v2, not v1.
- Implementation lands under `impl/`; research under `research/`. The moat `impl/test-derivation-engine/src/rules/` stays **private** — never publish to public `arcanum/`.
- REFORMULATE imports are copied to unblock the build, then re-authored for v2's *govern+enforce Ontology A on evidence* mandate (tracked in `IMPORT-MANIFEST.md`); the 4 DROP capabilities are never imported.
- Public/private submodule discipline still applies (see
  [`SUBMODULE-DISCIPLINE.md`](../../SUBMODULE-DISCIPLINE.md)).
