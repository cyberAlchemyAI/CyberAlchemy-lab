# DomainSpec v2 development migration inventory

> Generated from `inventory.json`. The JSON is canonical; this file is a human projection.

## Result

Important development material was not moved, but copying the whole development tree would mix admitted baseline dependencies, active writer-owned work, historical evidence, and generated residue.

- Development directories: **58**
- Git-tracked files: **9190**
- Untracked nonignored files: **3908**
- Ignored files: **15510**
- Ledger artifacts under development: **126**
- Frozen baseline inventory: **771 files; 766 current source paths present, 5 paths missing**
- Exact baseline state: **742 exact, 24 current source members drifted from the admitted hashes**

## Confirmed gaps

- **DEV-GAP-01** — The admitted baseline inventory has 771 members; 766 current source bytes are present in Craft and 5 development paths are absent.
- **DEV-GAP-02** — The admitted baseline is also semantically stale against 24 current source members. Those same current bytes were copied exactly into Craft, so this is source-baseline drift, not Craft-only drift.
- **DEV-GAP-03** — The baseline manifest, owner decision, validator, ontology current-state views, and materializer remain outside Craft, so the copied current-definition projections do not have local validation closure.
- **DEV-GAP-04** — The copied Craft ledger still addresses 126 development artifacts that were excluded from the transplant.
- **DEV-GAP-05** — Active writer-owned work exists in evf-reference-consumer, evolvable-validation-framework and must not be silently frozen by this inventory.
- **DEV-GAP-06** — Ignored and generated build residue is evidence of local execution state, not a migration candidate.

## Baseline bridge inputs

These records are required to preserve and explain the old baseline epoch. Because 24 source members have drifted, they must not be rebound as the current baseline without a successor-baseline decision.

- `projects/domainspec-v2/development/meta-type-instantiation-cli/CANONICAL-IMPLEMENTED-BASELINE.v2.json` — missing
- `projects/domainspec-v2/development/meta-type-instantiation-cli/OWNER-CANONICAL-DOCS-AND-BASELINE-V2-DECISION.json` — missing
- `projects/domainspec-v2/development/meta-type-instantiation-cli/validate-baseline.mjs` — missing
- `projects/domainspec-v2/development/implementation-conformance/ontology-experiment/ontology.json` — missing
- `projects/domainspec-v2/development/implementation-conformance/ontology-experiment/domain-meta-types.projection.json` — missing
- `projects/domainspec-v2/development/implementation-conformance/ontology-experiment/materialize-current-meta-type-state.mjs` — missing

Missing frozen inventory members:

- `projects/domainspec-v2/development/backend-meta-type-conformance/evidence/WP-BMC-001/BMC-EVD-001.MATURITY-MATRIX.json`
- `projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json`
- `projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json`
- `projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/rust-strict.profile.json`
- `projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json`

Baseline validator execution:

- **not_evaluable** — `node` is not available on the current shell PATH; no runtime validator claim is made.

## Directory classification

| Directory | Tracked | Untracked | Ignored | Ledger | Stable refs | Baseline | Lane | Tier | Recommendation |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| `2026-07-06-write-right-share-substrate` | 4 | 0 | 0 | 0 | 0 | 0 | product-construction-or-evidence | T3_UNREFERENCED_DEVELOPMENT_HISTORY | retain in source history; do not copy by default |
| `agent-spec-conformance` | 2 | 0 | 0 | 1 | 2 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `architecture-pattern-enforcement` | 2149 | 0 | 236 | 7 | 14 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `architecture-realization-compiler` | 16 | 0 | 19 | 0 | 14 | 0 | product-construction-or-evidence | T2_REFERENCED_DEVELOPMENT_HISTORY | preserve externally or migrate only with the referencing surface |
| `backend-cli-completion` | 17 | 0 | 0 | 0 | 0 | 0 | product-construction-or-evidence | T3_UNREFERENCED_DEVELOPMENT_HISTORY | retain in source history; do not copy by default |
| `backend-meta-type-conformance` | 2 | 0 | 0 | 2 | 6 | 1 | product-construction-or-evidence | T0_REQUIRED_BASELINE_CLOSURE | author an exact dependency-closed copy and path-rebinding candidate |
| `code-tag-conformance` | 5 | 0 | 0 | 1 | 2 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `completeness-audit` | 9 | 0 | 0 | 0 | 0 | 0 | product-construction-or-evidence | T3_UNREFERENCED_DEVELOPMENT_HISTORY | retain in source history; do not copy by default |
| `compound-domain-structure-calibration` | 407 | 0 | 0 | 0 | 1 | 0 | product-construction-or-evidence | T2_REFERENCED_DEVELOPMENT_HISTORY | preserve externally or migrate only with the referencing surface |
| `comprehension-novice-test` | 8 | 0 | 0 | 0 | 4 | 0 | product-construction-or-evidence | T2_REFERENCED_DEVELOPMENT_HISTORY | preserve externally or migrate only with the referencing surface |
| `decisions` | 1 | 0 | 5 | 0 | 0 | 0 | product-construction-or-evidence | T3_UNREFERENCED_DEVELOPMENT_HISTORY | retain in source history; do not copy by default |
| `definitions-governance-enhancement` | 3 | 0 | 0 | 0 | 2 | 0 | product-construction-or-evidence | T2_REFERENCED_DEVELOPMENT_HISTORY | preserve externally or migrate only with the referencing surface |
| `ds-d1-improvement-plan` | 26 | 0 | 0 | 0 | 2 | 0 | product-construction-or-evidence | T2_REFERENCED_DEVELOPMENT_HISTORY | preserve externally or migrate only with the referencing surface |
| `durable-compensation-concepts` | 4 | 0 | 0 | 0 | 2 | 0 | product-construction-or-evidence | T2_REFERENCED_DEVELOPMENT_HISTORY | preserve externally or migrate only with the referencing surface |
| `evf-factory-obligation-evidence-adapter` | 22 | 0 | 2 | 0 | 0 | 0 | product-construction-or-evidence | T3_UNREFERENCED_DEVELOPMENT_HISTORY | retain in source history; do not copy by default |
| `evf-reference-consumer` | 0 | 377 | 0 | 0 | 0 | 0 | product-construction-or-evidence | HOLD_ACTIVE_WRITER | inventory now; freeze an immutable source epoch before any copy |
| `evolvable-validation-framework` | 635 | 3531 | 1163 | 9 | 30 | 0 | product-construction-or-evidence | HOLD_ACTIVE_WRITER | inventory now; freeze an immutable source epoch before any copy |
| `financial-settlement-executable-test-generation` | 128 | 0 | 0 | 0 | 0 | 0 | product-construction-or-evidence | T3_UNREFERENCED_DEVELOPMENT_HISTORY | retain in source history; do not copy by default |
| `first-production-release` | 595 | 0 | 31 | 50 | 21 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `formal-model-proof-provider` | 145 | 0 | 46 | 0 | 0 | 0 | product-construction-or-evidence | T3_UNREFERENCED_DEVELOPMENT_HISTORY | retain in source history; do not copy by default |
| `format-honesty` | 20 | 0 | 2 | 5 | 3 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `implementation-conformance` | 563 | 0 | 0 | 5 | 28 | 4 | product-construction-or-evidence | T0_REQUIRED_BASELINE_CLOSURE | author an exact dependency-closed copy and path-rebinding candidate |
| `invoke-define-cli-modeling-experiment` | 48 | 0 | 1 | 0 | 0 | 0 | product-construction-or-evidence | T3_UNREFERENCED_DEVELOPMENT_HISTORY | retain in source history; do not copy by default |
| `language-type-enforcement-parser-experiment` | 21 | 0 | 0 | 0 | 0 | 0 | product-construction-or-evidence | T3_UNREFERENCED_DEVELOPMENT_HISTORY | retain in source history; do not copy by default |
| `make-it-green` | 2 | 0 | 0 | 1 | 2 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `meta-type-closure-epoch` | 189 | 0 | 1704 | 0 | 0 | 0 | product-construction-or-evidence | T3_UNREFERENCED_DEVELOPMENT_HISTORY | retain in source history; do not copy by default |
| `meta-type-complete-implementation` | 44 | 0 | 0 | 0 | 0 | 0 | product-construction-or-evidence | T3_UNREFERENCED_DEVELOPMENT_HISTORY | retain in source history; do not copy by default |
| `meta-type-definitions` | 4 | 0 | 0 | 1 | 3 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `meta-type-factory-reproducibility` | 1 | 0 | 1062 | 1 | 6 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `meta-type-formalization` | 22 | 0 | 0 | 1 | 11 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `meta-type-implementation-depth` | 22 | 0 | 1 | 0 | 0 | 0 | product-construction-or-evidence | T3_UNREFERENCED_DEVELOPMENT_HISTORY | retain in source history; do not copy by default |
| `meta-type-instantiation-cli` | 34 | 0 | 0 | 4 | 20 | 0 | product-construction-or-evidence | T0_REQUIRED_BASELINE_CLOSURE | author an exact dependency-closed copy and path-rebinding candidate |
| `meta-type-realization-factory` | 0 | 0 | 63 | 1 | 9 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `ontology-form-decisions` | 32 | 0 | 30 | 2 | 8 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `operational-resilience-observability-deployment-integration` | 361 | 0 | 180 | 4 | 3 | 0 | operational-support | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `proof-obligation-substrate` | 1 | 0 | 0 | 1 | 3 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `r3-closeout-plan` | 52 | 0 | 0 | 0 | 4 | 0 | product-construction-or-evidence | T2_REFERENCED_DEVELOPMENT_HISTORY | preserve externally or migrate only with the referencing surface |
| `r3-l2-relationship-hardening` | 20 | 0 | 0 | 0 | 1 | 0 | product-construction-or-evidence | T2_REFERENCED_DEVELOPMENT_HISTORY | preserve externally or migrate only with the referencing surface |
| `r3-research` | 4 | 0 | 0 | 0 | 1 | 0 | product-construction-or-evidence | T2_REFERENCED_DEVELOPMENT_HISTORY | preserve externally or migrate only with the referencing surface |
| `refinement-runs` | 246 | 0 | 3134 | 9 | 40 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `reformulate-batch1` | 46 | 0 | 0 | 1 | 8 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `relationship-constraint-decisions` | 596 | 0 | 456 | 9 | 5 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `remaining-meta-types` | 79 | 0 | 5053 | 2 | 132 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `research` | 173 | 0 | 463 | 1 | 11 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `reviews` | 19 | 0 | 174 | 2 | 2 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `saga-removal` | 59 | 0 | 0 | 0 | 5 | 0 | product-construction-or-evidence | T2_REFERENCED_DEVELOPMENT_HISTORY | preserve externally or migrate only with the referencing surface |
| `spec-comprehension-model` | 5 | 0 | 0 | 0 | 3 | 0 | product-construction-or-evidence | T2_REFERENCED_DEVELOPMENT_HISTORY | preserve externally or migrate only with the referencing surface |
| `spec-ontology-branch-decision` | 536 | 0 | 35 | 3 | 6 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `specified-first-order-logic-framework` | 317 | 0 | 0 | 0 | 0 | 0 | product-construction-or-evidence | T3_UNREFERENCED_DEVELOPMENT_HISTORY | retain in source history; do not copy by default |
| `system-integration-contract-layer` | 176 | 0 | 1431 | 2 | 2 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `test-derivation-engine-next-epoch` | 793 | 0 | 219 | 0 | 4 | 0 | product-construction-or-evidence | T2_REFERENCED_DEVELOPMENT_HISTORY | preserve externally or migrate only with the referencing surface |
| `transactional-outbox-runtime` | 1 | 0 | 0 | 0 | 0 | 0 | product-construction-or-evidence | T3_UNREFERENCED_DEVELOPMENT_HISTORY | retain in source history; do not copy by default |
| `ui-candidate-formalization-experiments` | 69 | 0 | 0 | 0 | 1 | 0 | product-construction-or-evidence | T2_REFERENCED_DEVELOPMENT_HISTORY | preserve externally or migrate only with the referencing surface |
| `ui-meta-type-formalization` | 216 | 0 | 0 | 0 | 3 | 0 | product-construction-or-evidence | T2_REFERENCED_DEVELOPMENT_HISTORY | preserve externally or migrate only with the referencing surface |
| `ui-meta-type-repair` | 189 | 0 | 0 | 0 | 4 | 0 | product-construction-or-evidence | T2_REFERENCED_DEVELOPMENT_HISTORY | preserve externally or migrate only with the referencing surface |
| `ui-profile-implementation` | 45 | 0 | 0 | 1 | 10 | 0 | product-construction-or-evidence | T1_ACTIVE_LEDGER_EVIDENCE | migrate as a separately bounded evidence or product-history bundle |
| `validation-architecture-roadmap` | 3 | 0 | 0 | 0 | 1 | 0 | product-construction-or-evidence | T2_REFERENCED_DEVELOPMENT_HISTORY | preserve externally or migrate only with the referencing surface |
| `workflow-reflections` | 4 | 0 | 0 | 0 | 0 | 0 | product-construction-or-evidence | T3_UNREFERENCED_DEVELOPMENT_HISTORY | retain in source history; do not copy by default |

## Migration order

1. **Resolve the baseline epoch** — Review the 24 current-source changes against baseline v2 and choose a successor current-baseline candidate or an explicit restoration. Do not label baseline v2 current while this drift remains.
2. **Preserve the baseline bridge** — Author one exact historical bridge candidate for the six control-plane records plus the five missing frozen members, retaining their old identity and claim ceiling.
3. **Reconcile copied ledger references** — For every development artifact reference, choose local migration, explicit external source binding, or deliberate retirement; never leave an accidental broken local path.
4. **Freeze active writer-owned work** — Create a new immutable source epoch for EVF and the EVF reference consumer only after their current owner declares the selected bytes stable.
5. **Migrate bounded product and evidence bundles** — Move T1 bundles by dependency closure and lane, keeping product-construction evidence separate from operational-support residue.
6. **Retain history without bulk copying** — Keep T2 and T3 development history at an explicit source locator unless a live consumer proves it is needed.

## Claim ceiling

This inventory proves only the observed source population, exact current baseline gap, ledger-addressed surfaces, and migration classifications at this source epoch. It does not accept, admit, copy, rebind, activate, publish, release, deploy, or retire any artifact.
