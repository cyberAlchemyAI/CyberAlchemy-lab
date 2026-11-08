---
node_type: craft-view
title: CRAFT — DomainSpec v2
status: active
updatedAt: 2026-08-29
---

# CRAFT — DomainSpec v2

> Human view of [`.craft/ledger.yml`](.craft/ledger.yml), the source of truth. This export changes no product, authority, promotion, publication, release, deployment, or production state.

## Current frontier

The exact current meta-type implementation is frozen and owner-admitted for project-local CLI development as `domainspec-meta-types-current-implemented@2`, baseline digest `10c29c2a4feb5039b6c90dcd7e2d44024757b4dd2414f9c0383c82387ec6e836`. Its 771-file inventory binds the canonical definition state, all 13 active backend types, 39 TypeScript/Python/Rust realization rows, 11 UI state rows and their supporting kernel, family, factory and acceptance evidence. A first-class 16-row enforcement-asset registry now separates the frozen input, selected candidate-3 contract, evidence repairs, target findings, state drift and missing product machinery. `SWU-MTCLI-003` is selectable but not selected. Publication, release, deployment and production remain unauthorized.

- Open decisions: none
- Active blockers: `BLK-DSV2-DRIFT-ENGINE`, `BLK-DSV2-L2-ATTESTATION`, `BLK-DSV2-SMO-ARCANUM-BINDING`, `BLK-DSV2-SICL-REV2-REFRESH`, `BLK-DSV2-P2-DENOMINATOR-DRIFT`, `BLK-DSV2-REFINE-PLAN-ADMISSIBILITY`, `BLK-DSV2-SPEC-ONTOLOGY-VERIFIER-ADMISSION`, `BLK-DSV2-PROOF-GATE01-BINDING`, `BLK-DSV2-EVF-P0-EXECUTION-ADMISSION`, `BLK-DSV2-ORODI-LIVE-BINDINGS`, `BLK-DSV2-BMC-REL-PREACCEPTANCE-CLOSURE`
- Active gaps: `GAP-SH-UI11-MIGRATE`, `GAP-SH-PROSE-HOMES`, `FR-FPR-ONTOLOGY-DIRECTION`, `FR-FPR-SOLVER-PROFILE`, `FR-FPR-BW-ORIGIN-ROUTE`, `FR-FPR-I-ROOT-DISPOSITIONS`, `FR-FPR-APE-SELF-CONTAINMENT`, `GAP-DSV2-SFC-UNEXECUTED`, `GAP-DSV2-FMP-UNSELECTED`, `GAP-DSV2-FMP-TRACE`, `GAP-DSV2-TWO-LANE-INTEGRATION`, `GAP-DSV2-SFC-004-FUSED`, `GAP-DSV2-CARD-EDGE-DRIFT`, `GAP-DSV2-BMC-REALIZATION-BINDINGS`, `GAP-DSV2-FMT-SWU001-CLOSEOUT`, `GAP-DSV2-EVF-SMT-PROVIDER`, `GAP-DSV2-ORODI-TOOL-PROFILE-ADMISSION`, `GAP-DSV2-META-TYPE-TARGET-ENFORCEMENT`

## Meta-type state

Machine source: [`.craft/artifacts/META-TYPE-STATE.json`](.craft/artifacts/META-TYPE-STATE.json). Freshness check: [`.craft/artifacts/validate-meta-type-state.mjs`](.craft/artifacts/validate-meta-type-state.mjs).

The canonical starting point is `domainspec-meta-types-current-implemented@2`, digest `10c29c2a4feb5039b6c90dcd7e2d44024757b4dd2414f9c0383c82387ec6e836`: 771 frozen evidence files, 13 active backend meta-types, 13 family roots, 39 TypeScript/Python/Rust realization rows, 11 differentiated UI state rows, 31 authority/audit relationship rows and 17 backend-implementation relationship rows. The baseline is admitted, but exact target implementation enforcement: **missing**. The historical BMC matrix still records 30 snapshot binding findings and later Rule changes still explain six source/provider digest drifts, but those are provenance rather than admission gates for baseline v2.

### Backend types

| Meta-type | Realizations | Snapshot provider registration | Profile / ontology | Freshness and gap |
| --- | ---: | ---: | --- | --- |
| `DS-D1.1` Entity | TS / Python / Rust | 3/3 | profile absent; ontology blocked | Snapshot current; queue not ready. |
| `DS-D1.2` Value Object | TS / Python / Rust | 3/3 | profile absent; ontology blocked | Three stale candidate bindings. |
| `DS-D1.3` Enum | TS / Python / Rust | 3/3 | separate non-uniform precedent; ontology blocked | Nine absent candidate bindings. |
| `DS-D1.4` Operation | TS / Python / Rust | 0/3 | candidate-local uniform anchor; ontology blocked | Candidate current; providers unregistered; queue not ready. |
| `DS-D1.5` Query | TS / Python / Rust | 3/3 | profile absent; ontology blocked | Six absent candidate bindings. |
| `DS-D1.6` Calculation | TS / Python / Rust | 3/3 | profile absent; ontology blocked | Six absent candidate bindings. |
| `DS-D1.7` Rule | TS / Python / Rust | 0/3 | profile absent; ontology blocked | BMC snapshot stale for all three source/provider pairs. |
| `DS-D1.8` Policy | TS / Python / Rust | 3/3 | profile absent; ontology blocked | Six absent candidate bindings. |
| `DS-D1.9` Workflow | TS / Python / Rust | 0/3 | candidate-local uniform anchor; ontology blocked | Candidate current; providers unregistered; queue not ready. |
| `DS-D1.11` Interface | TS / Python / Rust | 0/3 | profile absent; ontology blocked | Candidate current; providers unregistered; queue not ready. |
| `DS-D1.12` Event | TS / Python / Rust | 0/3 | profile absent; ontology blocked | Candidate current; providers unregistered; queue not ready. |
| `DS-D1.13` Mapping | TS / Python / Rust | 0/3 | profile absent; ontology blocked | Candidate current; providers unregistered; queue not ready. |
| `DS-D1.14` State Machine | TS / Python / Rust | 0/3 | profile absent; ontology blocked | Candidate current; providers unregistered; queue not ready. |

All 13 are canonically active as meta-types and their exact realization evidence is admitted by the frozen baseline. “0/3 registered” and the 0-ready/13-blocked queue above are historical BMC/ontology-source states, not absence of implementation files and not prerequisites for baseline v2. A changed frozen byte requires a new baseline version.

### UI types

| Meta-type | Current state | Development formation | Authority boundary |
| --- | --- | --- | --- |
| `DS-D1.15` Page | candidate | `impl/spec/meta-types/ui/page.schema.yml` | owner review required |
| `DS-D1.16` Layout | candidate | `impl/spec/meta-types/ui/layout.schema.yml` | owner review required |
| `DS-D1.17` Component | candidate | `impl/spec/meta-types/ui/component.schema.yml` | owner review required |
| `DS-D1.18` View Model | candidate | `impl/spec/meta-types/ui/view-model.schema.yml` | owner review required |
| `DS-D1.19` Hook | candidate | `impl/spec/meta-types/ui/hook.schema.yml` | owner review required |
| `DS-D1.20` Form | candidate | `impl/spec/meta-types/ui/form.schema.yml` | owner review required |
| `DS-D1.21` Action | candidate | `impl/spec/meta-types/ui/action.schema.yml` | owner review required |
| `DS-D1.22` Guard | candidate | `impl/spec/meta-types/ui/guard.schema.yml` | owner review required |
| `DS-D1.23` Binding | candidate | `impl/spec/meta-types/ui/binding.schema.yml` | owner review required |
| `DS-D1.24` Adapter | deferred / merge candidate | `impl/spec/ui-profile/concepts/adapter.yml` | alias-to-Mapping versus independent-node versus defer is unresolved |
| `DS-D1.25` State Indicator | deferred / split candidate | `impl/spec/ui-profile/concepts/state-indicator.yml` | split, independent node, new identities or defer is unresolved |

The UI work pack and aggregate validation are development evidence only. They do not activate DS-D1 members, settle DS-D8 relationship residues or add the UI types to the supported backend profile.

### Operation contract

The `DS-D1.4` candidate and its three language realizations express the declared read/write/effect sets; guard-before-mutation; atomic state-and-outbox behavior; explicit failure continuation; rejection of undeclared reads, writes and effects; and blueprints connecting Operation to Rule, Event, Interface and Workflow. The four relationship blueprints and the transaction/effect-group handle remain unmaterialized, the three providers remain unregistered, and ontology admission is absent. What is still missing is the generated-project machinery that pins an admitted Operation realization and then observes the target project’s real implementation, failing closed on any structure, relationship, effect, order, continuation or digest mismatch.

## Meta-type enforcement assets

Machine registry: [`.craft/artifacts/META-TYPE-ENFORCEMENT-ASSETS.json`](.craft/artifacts/META-TYPE-ENFORCEMENT-ASSETS.json). Contract: [schema](.craft/artifacts/meta-type-enforcement-assets.schema.json). Freshness check: [validator](.craft/artifacts/validate-meta-type-enforcement-assets.mjs).

| Asset | Class / state | Exact boundary |
| --- | --- | --- |
| `MTENF-BASELINE-V2` | canonical baseline / frozen pass | Immutable 771-file, 13-type, 39-realization input; not instantiation machinery. |
| `MTENF-INSTANTIATE-CONTRACT-C3` | contract / validated pass | SWU-MTCLI-002 closed at 17/17; implementation and target conformance remain false. |
| `MTFIX-VALUE-OBJECT-BINDINGS` | repair / flagged | Three stale candidate bindings; no proven defect in admitted Value Object source bytes. |
| `MTFIX-ENUM-BINDINGS` | repair / flagged | Nine absent candidate bindings; no evidence that the three admitted Enum realizations are missing. |
| `MTFIX-RULE-EVIDENCE-DRIFT` | evidence refresh / stale | Refresh the snapshot for six Rule source/provider digest changes; do not repair baseline bytes from this evidence alone. |
| `MTFIND-OPERATION-AOP-BOUNDARY` | target finding / unresolved | Preserve `AOP_BOUNDARY_INSTRUMENTATION_PLACEMENT`; the evaluator passes while its selected target fails. |
| `MTFIND-WORKFLOW-COMPENSATION` | target finding / unresolved | Preserve `AOP_WF_COMPENSATION_CALLABLE_MISSING`; the evaluator passes while its selected target is incomplete. |
| `MTFIX-FRONTIER-POINTER-DRIFT` | state drift / refresh required | Candidate-3 makes SWU-MTCLI-003 next; older work-pack/current-state pointers still name SWU-MTCLI-002. |
| `MTM-CATALOG` | machinery / selectable, not selected | Select one exact frozen realization row and digests under SWU-MTCLI-003. |
| `MTM-DECODER` | machinery / not implemented | Closed node, body and relationship vocabulary; unknown or extra input fails closed. |
| `MTM-PLANNER` | machinery / not implemented | Deterministic contained artifact plan before filesystem mutation. |
| `MTM-WRITER` | machinery / not implemented | Guarded create-only, collision-safe, atomic target publication. |
| `MTM-RECEIPT` | machinery / not implemented | D35 baseline/input/selection/plan/output/reread binding and CLI surface. |
| `MTM-GENERALIZATION` | machinery / not implemented | Exact 13-meta-type by three-language generation coverage. |
| `MTM-RELATIONSHIP-OBSERVER` | machinery / not implemented | Read/write/effect sets, guard order, atomicity, continuation and Rule/Event/Workflow relationship observation. |
| `MTM-PACKAGE` | machinery / not implemented | Normal aggregate wiring, private package and clean-root deterministic replay. |

The registry is operational state under existing definitions D31–D35. Candidate binding drift is not a canonical source defect; a target finding is not an evaluator defect; planned machinery is not implemented. Changing a frozen definition, source, provider or binding byte requires a successor baseline. This registry has `baseline_effect: none` and `authority_effect: none`.

### Machinery and direct consumers

| State owner | Stage / gate | Current boundary |
| --- | --- | --- |
| `CTX-DSV2-META-TYPE-FORMALIZATION` | `build / flag` | 13 backend formations and content validation exist; UI formation and extraction residue remain. |
| `CTX-DSV2-SPEC-ONTOLOGY` | `design / block` | Connected-graph architecture is selected; verifier admission and structural verification remain. |
| `CTX-DSV2-ONTOLOGY-FORMS` | `validated / pass` | The historical 0-ready/13-blocked queue is retained as provenance; the owner admitted the exact current implementation as baseline v2 after canonical definitions and ontology, so its form rows are not reopened. |
| `CTX-DSV2-RMT` | `validated / pass` | Seven-type candidate-local proof and receipt reconciliation pass; original 70 Task Session units were not executed. |
| `CTX-DSV2-APE` | `validate / flag` | Operation/Workflow prototype sequences pass at their ceiling; Enum W2, parity and scaling remain. |
| `CTX-DSV2-MTF` | `validated / pass` | Legacy nine-node, same-host reproducibility proof only. |
| `CTX-DSV2-REALIZATION-KERNEL` | `validated / pass` | The exact 771-file canonical-definition plus 13-family/39-row implementation surface is frozen and owner-admitted for CLI consumption. |
| `CTX-DSV2-SICL` | `validated / flag` | Generic-factory candidate passes; authorized Refresh remains before target selection. |
| `CTX-DSV2-SMO` | `plan / block` | 325 obligation cells and 31 relationship rows are planned; live bindings, admission and eight residual gates remain. |
| `CTX-DSV2-FMP` | `plan / flag` | Eight-SWU TLA/TLC plan is selection-ready; no live formal-provider execution or trace proof. |
| `CTX-DSV2-PROOF-OBLIGATION-SUBSTRATE` | `validate / block` | Syntax adoption accepted; refreshed GATE-01 binding remains. |
| `CTX-DSV2-IMPL-CONFORMANCE` | `design / flag` | Candidate-3 closes `SWU-MTCLI-002`; the 16 enforcement assets separate repairs, findings and machinery; `SWU-MTCLI-003` is selectable but not selected. |
| `CTX-DSV2-EVF` | `validate / block` | Bounded L0/L1/L2 evidence passes; retained owner/readiness and optional provider gates remain. |
| `CTX-DSV2-FORMAT-HONESTY` | `validate / flag` | Checker passes and exposes 49 findings; SWU-FMT-001 closeout and card generation remain. |
| `CTX-DSV2-BMC` | `validate / flag` | Historical maturity snapshot has 30 binding findings plus later Rule drift; refresh and BMC-OBS remain. |
| `CTX-DSV2-BMC-REL` | `preacceptance / block` | N05/N45 closed; post-repair review, two real closure runs, graph freeze and graph review remain. |
| `CTX-DSV2-FIRST-PRODUCTION-RELEASE` | `plan / block` | RMT/SFC inputs exist; 17/17 profile admission, two-lane integration and five release frontiers remain. |
| `CTX-DSV2-FPR02-BACKEND` | `plan / block` | Development BTE reaches 17/91; matching independent red-manifest freeze and L0B authority remain. |
| `CTX-DSV2-FPR02-UI` | `build / flag` | Development UI work pack passes; canonical authority deltas remain owner-gated. |
| `CTX-DSV2-FPR02B-CONSUMER-PROOF` | `plan / block` | Historical L0A and byte repair pass; independent red freeze and Refresh remain. |
| `CTX-DSV2-SFC` | `plan / flag` | Candidate profile is 13 kinds / 17 relationships; SFC projections remain at 16 and admission/implementation are absent. |

The next complete vertical slice is product implementation, not another governance campaign: version the current no-write CLI contract, project the frozen catalog, decode one Entity node, deterministically plan and publish a TypeScript instantiation into a new empty target root, emit a baseline-bound receipt, re-read it, and fail closed on any mismatch. Later waves generalize the same machinery to all 13 types and three languages, then add Operation relationship/effect/continuation observation and clean-root package evidence.

## Contexts

| Context | Parent | Stage / gate | Purpose |
| --- | --- | --- | --- |
| `CTX-DSV2-ROOT` — DomainSpec v2 — implementation home | `root` | `build` / `flag` | v2 rework of the DomainSpec pillar (the *what* — typed intent -> engine / Lean kernel). The implementation home: import + reformulate from v1 (frozen evidence source) under the mandate "govern + enforce Ontology A on evidence". Recomposes into cav2 CTX-CAV2-DOMAINSPEC-V2. |
| `CTX-DSV2-AUTHORITY` — Minted authority spine (3 governances) | `CTX-DSV2-ROOT` | `minted` / `flag` | The cav2 authority MOLD cast onto v2: 3 domain-originated governances (validation / layering / drift), the recursion model (muF law/check + nuF drift), the credibility constitution + the per-governance split plan. |
| `CTX-DSV2-MAKE-IT-GREEN` — Make impl/ green (L0-L3) | `CTX-DSV2-ROOT` | `validated` / `flag` | Make the forked engine + governance tooling buildable and green in v2, and wire the validation-governance gate (C9/C10/C11). |
| `CTX-DSV2-REFORMULATE-BATCH1` — Reformulate the 6 Batch-1 spec docs (v1 -> v2) | `CTX-DSV2-ROOT` | `plan` / `flag` | Re-author AXIOMS / TAXONOMY / RELATIONSHIPS / TEST-PIPELINE / DRIFT-CONVERGENCE / CONSTITUTION from v1-verbatim to v2-native, bound to their governance owners; closes the v1-freeze gate. |
| `CTX-DSV2-SPEC-ONTOLOGY` — Specification-ontology branch architecture | `CTX-DSV2-ROOT` | `design` / `block` | Decide whether the v2 spec surface (aspect files + TAXONOMY + RELATIONSHIPS) is a system ontology, and whether "spec == ontology" (SEED Lane Z) is worth pursuing. |
| `CTX-DSV2-META-TYPE-FORMALIZATION` — Meta-type formalization (checkable type system + content validator) | `CTX-DSV2-REFORMULATE-BATCH1` | `build` / `flag` | Formalize the staged DS-D1 candidate catalog into checkable well-formedness criteria (by category) + the edge signatures, and build the content validator that checks an aspect file by types + edges. The backend 13 are shape/fixture-backed candidates; the UI 11 remain formation-deferred. Makes the toy's M1 mechanical; feeds batch-1 R2 (TAXONOMY formal criteria) + R7 (DS-D1 system definition). |
| `CTX-DSV2-APE` — Architecture-pattern enforcement (APE) — validate + enforce patterns across projects | `CTX-DSV2-ROOT` | `validate` / `flag` | Sequence the owned architecture-validation pieces (meta-type schemas, edge-law, validators, engine, v1 pattern-library) into an enforced discipline: node plane (uniformity), R3A root edge-law authority, downstream composability enforcement, authority promotion via cav2, cross-project inheritance via mint. A candidate discipline — every handle owes owner-promotion ("has a tree != has authority"). |
| `CTX-DSV2-CODE-TAG-CONFORMANCE` — Code-tag conformance (Batch-2) — root authority + machine schema + one gate | `CTX-DSV2-ROOT` | `build` / `flag` | Finish the R0 migration across the whole code-tag / C6 code<->spec binding subsystem: taxonomy from root schemas (CT-1), tag contract as code-tag.schema.yml (CT-2), waiver reset + v1-path fix (CT-3), fold into the unified validate gate (CT-4). The deferred Batch-2 code-tag reformulation, now planned. |
| `CTX-DSV2-AGENT-SPEC-CONFORMANCE` — Agent⊨spec conformance — runtime action↔spec plane (L3), general core + witnesses | `CTX-DSV2-ROOT` | `design` / `flag` | Build a general agent⊨spec verifier: a domain-agnostic core (spec, action) -> conform | not-conform + counter-witness + safe-fallback, with thin per-domain plug-ins. The Layer-3 runtime plane that meta-type-formalization explicitly deferred (its non-goal). Build-from-owned on the v2 consume-root/contract-as-schema/one-gate pattern; a distinct plane beside code-tag (L1 binding) and meta-type (L1 content) — NOT a merge. |
| `CTX-DSV2-FIRST-PRODUCTION-RELEASE` — DomainSpec v2 first production release | `CTX-DSV2-ROOT` | `plan` / `block` | Carry the accepted private repository-local system-builder and conformance CLI from owner-ratified business meaning through typed specification projection, architecture and composable-pattern enforcement, bounded formal validation, independently grounded generated verification, structural implementation analysis, directional cross-graph conformance, a clean release candidate, and the exact 14-step Body War pilot. This context is continuation authority, not production authorization. |
| `CTX-DSV2-FPR02-BACKEND` — FPR-02B backend profile and pilot lane | `CTX-DSV2-FIRST-PRODUCTION-RELEASE` | `plan` / `block` | Freeze the exact backend-only supported profile, product surface, claims, callback and origin posture, redaction rules, rollback route, and accountable owners for the first production release. This lane excludes UI concepts and has no completion dependency on UI implementation. |
| `CTX-DSV2-FPR02-UI` — FPR-02U required UI development lane | `CTX-DSV2-FIRST-PRODUCTION-RELEASE` | `build` / `flag` | Implement and audit the 11 required UI meta-type concepts in a development-only lane, preserving the existing UI work-pack and routing all authority deltas to their owners. This lane neither enters nor blocks the backend first-release profile. |
| `CTX-DSV2-FPR02B-CONSUMER-PROOF` — FPR-02B integrated engine and consumer proof | `CTX-DSV2-FPR02-BACKEND` | `plan` / `block` | Continue the accepted backend profile decision through one bounded BTE implementation route and independent read-only IOLM and Body War consumer proofs. This context indexes receipts and continuation; it does not become engine, graph, semantic, or production authority. |
| `CTX-DSV2-FPR-VISIBILITY` — First-production-release visibility and generated roadmap | `CTX-DSV2-FIRST-PRODUCTION-RELEASE` | `validated` / `pass` | Make the FPR dependency graph, current Craft gate, active research frontiers, exact Body War critical sequence, and evidence paths visible through deterministic JSON and self-contained HTML read models. The feature projects authority; it does not own continuation state or authorize production. |
| `CTX-DSV2-RMT` — Remaining meta-types (WP-RMT-002R reconciliation closed) | `CTX-DSV2-ROOT` | `validated` / `pass` | Record the exact seven-type candidate-local prototype governance reconciliation as closed without inventing the original 70 Task Session executions. Product bytes, candidates, proof receipts, registry and ontology were not changed by reconciliation. |
| `CTX-DSV2-SFC` — Stable foundation CLI (WP-SFC-001) — Lane B of the 2026-08-16 owner selection | `CTX-DSV2-FIRST-PRODUCTION-RELEASE` | `plan` / `flag` | Author and later execute a private, pre-production DomainSpec v2 CLI foundation bound to the broad P2 backend profile and an exact-profile causal implementation-conformance claim. It is subordinate to the accepted product-release contract and is not the 0.1.0 product. |
| `CTX-DSV2-STABILITY-REVIEW` — Production-stability baseline review (2026-08-14) | `CTX-DSV2-FIRST-PRODUCTION-RELEASE` | `validated` / `pass` | Establish, by red-team review over a frozen corpus, whether any current DomainSpec v2 artifact is production-stable, and if not, what the smallest honest candidate would be. |
| `CTX-DSV2-ONTOLOGY-FORMS` — Ontology form decisions (frozen baseline provenance) | `CTX-DSV2-META-TYPE-FORMALIZATION` | `validated` / `pass` | Preserve the historical decision matrix and queue while binding the owner's exact baseline-v1 selection; future changes version the baseline rather than reopening its rows. |
| `CTX-DSV2-SICL` — System-integration contract layer (SIC-FAC-000) | `CTX-DSV2-ROOT` | `validated` / `flag` | Adapt the architecture-conformance factory to system-integration contracts and prove a generic-factory candidate against a declared validation surface. |
| `CTX-DSV2-SMO` — Shared meta-obligation product readiness (WP-SMO-001) | `CTX-DSV2-ROOT` | `plan` / `block` | Build one shared obligation envelope covering all 13 active backend meta-types through 25 obligation families, with Cedar confined to authorization and Souffle confined to a finite typed batch graph profile. |
| `CTX-DSV2-FMP` — Formal-model proof provider (WP-FMP-001, finite TLA/TLC evidence) | `CTX-DSV2-ROOT` | `plan` / `flag` | Add a tla-tlc-model-evidence-v1 provider to the existing architecture-conformance factory, reusing its lock, snapshot, accounting, replay, verification, reproduction and receipt owners rather than building a parallel proof system. |
| `CTX-DSV2-IMPL-CONFORMANCE` — Implementation conformance and meta-type instantiation CLI | `CTX-DSV2-ROOT` | `design` / `flag` | Build the product machinery that consumes the frozen baseline, instantiates exact meta-type realizations in external projects, emits receipts and observes target conformance without granting publication, release or deployment. |
| `CTX-DSV2-EVF` — Evolvable validation framework | `CTX-DSV2-ROOT` | `validate` / `block` | Own the evolving evidence chain from DomainSpec meaning through formal obligation, implementation binding, executable or formal evaluation, and bounded receipt, while preserving semantic and provider ownership. |
| `CTX-DSV2-MTF` — Legacy meta-type factory reproducibility | `CTX-DSV2-ROOT` | `validated` / `pass` | Preserve the 2026-08-07 same-host nine-node reproducibility proof without treating it as the owner of the newer realization kernel and family implementations. |
| `CTX-DSV2-REALIZATION-KERNEL` — Frozen meta-type realization kernel and families | `CTX-DSV2-ROOT` | `validated` / `pass` | Hold the owner-admitted 771-file baseline with canonical definitions, 13 active backend family roots and 39 TypeScript/Python/Rust realization rows; generated-project enforcement remains a separate product frontier. |
| `CTX-DSV2-FORMAT-HONESTY` — Format honesty and generated meta-type cards (WP-FMT-001) | `CTX-DSV2-ROOT` | `validate` / `flag` | Remove hand-maintained copies of derived facts from the DomainSpec v2 surface. Two defects of the same class were found 2026-08-19: a file's extension does not predict its parser (49 of 204 .yml files contain JSON), and 8 of 13 meta-type cards disagree with the live relationship authority. The pack makes machine files honestly named, promotes documentation comments to typed fields, and generates the human cards so the copies cannot drift again. |
| `CTX-DSV2-BMC` — Backend meta-type conformance (WP-BMC-001) | `CTX-DSV2-ROOT` | `validate` / `flag` | Hold exact maturity evidence for all 13 backend meta-types and their 39 TypeScript/Python/Rust realization rows, then harden structural observation without confusing candidate evidence with profile or ontology admission. |
| `CTX-DSV2-BMC-REL` — Relationship constraint owner decisions (BMC-REL-001) | `CTX-DSV2-BMC` | `preacceptance` / `block` | Resolve non-numeric and later numeric semantics for the exact 31 active relationship signatures without inventing cardinality, closure, duplicate, self-edge, order, inverse, or representation policy. |
| `CTX-DSV2-PROOF-OBLIGATION-SUBSTRATE` — Proof-obligation cross-boundary substrate | `CTX-DSV2-ROOT` | `validate` / `block` | Adopt one exact structural address envelope for DomainSpec v2 proof-obligation references while preserving DomainSpec meaning/lifecycle ownership and transferring no authority to the private CAV2 spine. |
| `CTX-DSV2-ORODI` — Operational resilience, observability and deployment integration | `CTX-DSV2-ROOT` | `plan` / `block` | Turn accepted research into separately owned definition, design and non-executing planning artifacts without inventing live bindings or deployment authority. |

## Pending by node

### `CTX-DSV2-ROOT` — DomainSpec v2 — implementation home

`DEC-DSV2-META-TYPE-CANONICAL-DOCS-BASELINE-V2` admits the exact 2026-08-29 implementation as project-local canonical baseline `domainspec-meta-types-current-implemented@2`: canonical D31-D35 vocabulary, 13 backend types, 39 TypeScript/Python/Rust rows, 11 UI state rows and 771 frozen evidence files at digest `10c29c2a4feb5039b6c90dcd7e2d44024757b4dd2414f9c0383c82387ec6e836`. Candidate-3 closes the bounded instantiate contract; the product frontier is explicit selection of `SWU-MTCLI-003`. No generated-target conformance, publication, release, deployment or production claim follows.

Current execution is superseded to the pinned Node `26.8.1` container by `DSV2-NODE-26-RUNTIME-2026-08-29`; the runtime migration changes none of the 771 frozen `@2` implementation bytes. Node 22/24 receipts and decisions remain exact historical evidence, while [`RUNTIME.json`](RUNTIME.json) and [`validate-runtime.mjs`](validate-runtime.mjs) control current execution drift.

Owned artifacts: `ART-DSV2-IMPORT-MANIFEST`, `ART-DSV2-IMPL`, `ART-DSV2-AUTHORITY`, `ART-DSV2-META-TYPE-STATE`, `ART-DSV2-META-TYPE-STATE-VALIDATOR`, `ART-DSV2-META-TYPE-BASELINE-DECISION`, `ART-DSV2-META-TYPE-BASELINE`, `ART-DSV2-META-TYPE-CLI-PLAN`, `ART-DSV2-META-TYPE-ENFORCEMENT-ASSETS`, `ART-DSV2-META-TYPE-ENFORCEMENT-ASSETS-SCHEMA`, `ART-DSV2-META-TYPE-ENFORCEMENT-ASSETS-VALIDATOR`

### `CTX-DSV2-AUTHORITY` — Minted authority spine (3 governances)

SWU-R3C-010 L1 integrity receipt passes and is linked under authority/attestations/. Next R3 route is SWU-R3C-011 final verification. Full L2 remains blocked on external actor identity, key custody/signing, and a third-party verifier.

Owned artifacts: `ART-DSV2-AUTHORITY`, `ART-DSV2-RECURSION-RESEARCH`

### `CTX-DSV2-MAKE-IT-GREEN` — Make impl/ green (L0-L3)

G4 — wire `validate` + the fail-closed hook into CI/pre-commit (deferred).

Owned artifacts: `ART-DSV2-MAKE-IT-GREEN`, `ART-DSV2-IMPL`

### `CTX-DSV2-REFORMULATE-BATCH1` — Reformulate the 6 Batch-1 spec docs (v1 -> v2)

R0 DONE + DEC-B1-SATURN-AXIOM-SCOPE RESOLVED 2026-07-06 (scope-down-to-Saturn). R1 AXIOMS CLOSED 2026-07-10: authority/AXIOMS.{md,yml} is synchronized with CAV2-D49/D53/D54 and the impl/spec projection is gone. CT-1 code-tag taxonomy repair is done, so R2's validator-consumer landmine is closed. Next per DEC-DSV2-SPEC-HOMING: GAP-SH-UI11-MIGRATE -> verify-close R2 (delete TAXONOMY, gated on UI-11 migration) -> reconcile-close R7 -> R4/R5 -> R6a/R6b (crosswalk pre-decided by the axiom scope); then freeze gate.

Owned artifacts: `ART-DSV2-REFORMULATE-BATCH1`, `ART-DSV2-IMPORT-MANIFEST`

### `CTX-DSV2-SPEC-ONTOLOGY` — Specification-ontology branch architecture

DEC-DSV2-SPEC-ONTOLOGY-ARCHITECTURE-001 selected one connected semantic graph with separately owned business, formal-claims/specification, proof-bridge, and system branches. The exact @4 contract-hardening package passed candidate validation and Rondelli accepted all eleven owner slices, but every response remains verification-pending. Victor Boscaro's identity, verifier role/policy, and required V1/V2 receipts are absent; no protected role admission, checker execution, migration, implementation, promotion, or publication is authorized. Next: obtain the exact Victor @4 response and required structural verification, then materialize only the verified owner responses.

Owned artifacts: `ART-DSV2-SPEC-ONTOLOGY-RESEARCH`, `ART-DSV2-SPEC-ONTOLOGY-TOY`, `ART-DSV2-COMPOSABILITY-SYNTHESIS`

### `CTX-DSV2-META-TYPE-FORMALIZATION` — Meta-type formalization (checkable type system + content validator)

MT0-MT4 plus MT-INST are DONE for current backend scope: 13 node schemas, 31 active root relationship signatures, edge-aware validate-content, aggregate validate wiring, and instance generation/validation. The SGRM scoped-Workflow collapse migration is complete. Remaining: MT5 UI remains formation-deferred; the parallel ui-meta-type-formalization package is gathering candidate evidence without promotion authority. tools/lib extraction remains residue.

Owned artifacts: `ART-DSV2-META-TYPE-FORMALIZATION`

### `CTX-DSV2-APE` — Architecture-pattern enforcement (APE) — validate + enforce patterns across projects

The old SWU-APE-004/005 cleanup frontier is superseded. Operation AOP-001..010 and Workflow AWF-001..011 are terminal candidate-local prototype sequences with passing Work Pack verification; their evaluators preserve AOP_BOUNDARY_INSTRUMENTATION_PLACEMENT and AOP_WF_COMPENSATION_CALLABLE_MISSING. Enum W0 ontology closure and W1 TypeScript trust are complete. The nearest frontier is W2: SWU-APE-ENUM-PY-001 and SWU-APE-ENUM-RS-001 remain unselected until an exact user-confirmed parallel dispatch. W3 parity/closeout and W4 repeatable scaling remain after that. None of these receipts establishes synchronized Task Session closeout, profile admission, promotion, release, or production readiness.

Owned artifacts: `ART-DSV2-APE`

### `CTX-DSV2-CODE-TAG-CONFORMANCE` — Code-tag conformance (Batch-2) — root authority + machine schema + one gate

CT-1 DONE 2026-07-10 (taxonomy -> root schemas; batch-1 R2 code-tag deletion landmine closed). Next task-session CT-3, then CT-2, CT-4.

Owned artifacts: `ART-DSV2-CODE-TAG-CONFORMANCE`

### `CTX-DSV2-AGENT-SPEC-CONFORMANCE` — Agent⊨spec conformance — runtime action↔spec plane (L3), general core + witnesses

DEFINE + DESIGN authored (AV-D1 resolved -> 3-witness ramp dosage -> data-access -> robot; AV-D2 boundary = pipeline + plural certify-backends in core, domain in plug-in). Next: invoke plan -> work-pack over L0 (core + structural backend + dosage) -> L1 (data-access) -> L2 (runtime-monitor backend + robot). "general/moat" claim gates at L2 + decision-gate (AV-D4).

Owned artifacts: `ART-DSV2-AGENT-SPEC-CONFORMANCE`

### `CTX-DSV2-FIRST-PRODUCTION-RELEASE` — DomainSpec v2 first production release

FPR-01 and the UI development lane through SWU-UIP-007 are closed at their recorded ceilings. BTE has newer development-only 17-relationship/91-coverage green evidence, but the original independent-owner freeze and release gates remain unclosed. Lane A RMT reconciliation is terminal pass; Lane B SFC is source-fresh and selection-ready with no selected unit. Its once-absent complete-backend-criteria profile now exists as a 13-kind/17-relationship candidate, but it is not admitted or bound into the stale 16-relation SFC package. Next: re-ratify and refresh the 17/17 P2 denominator, bind/admit the selected profile, split fused SWU-SFC-004, and rerun the two-lane integration gate. The five FR-FPR-* frontiers and production prohibition remain.

Owned artifacts: `ART-DSV2-FPR-DECISION`, `ART-DSV2-FPR-RESEARCH`, `ART-DSV2-FPR-FINDINGS`, `ART-DSV2-FPR-ROADMAP`, `ART-DSV2-FPR-FRONTIER-MANIFEST`, `ART-DSV2-FPR-FOUNDATION-PLAN`, `ART-DSV2-FPR-FOUNDATION-ACTIVATION`, `ART-DSV2-FPR-SGRM007-ACTIVATION`, `ART-DSV2-FPR-SGRM007-REFRESH`, `ART-DSV2-FPR-W0-PROOF-SYNC-DECISION`, `ART-DSV2-FPR-W0-PROOF-REFRESH`, `ART-DSV2-FPR01-002-ADOPTION-ACTIVATION`, `ART-DSV2-FPR01-002-ACTIVATION-REFRESH`, `ART-DSV2-FPR01-002-RECEIPT`, `ART-DSV2-FPR01-002-RECEIPT-SYNC`, `ART-DSV2-FPR01-003-BASELINE`, `ART-DSV2-FPR01-003-VALIDATOR`, `ART-DSV2-FPR01-003-RECEIPT`, `ART-DSV2-FPR01-003-BLOCKER-SYNC`, `ART-DSV2-FPR01003-GUARD-RECEIPT`, `ART-DSV2-FPR01003-SAMPLE-RECEIPT`, `ART-DSV2-FPR01003-REPLAY-RESULT`, `ART-DSV2-FPR01003-PASS-SYNC`, `ART-DSV2-FPR01-004-RATIFICATION`, `ART-DSV2-FPR01-004-RECEIPT`, `ART-DSV2-FPR01-004-SYNC`, `ART-DSV2-FPR02-LANE-CONTRACT`, `ART-DSV2-FPR02-LANE-REFRESH`

### `CTX-DSV2-FPR02-BACKEND` — FPR-02B backend profile and pilot lane

Historical L0A and its exact-byte repair pass. New dirty-baseline reconciliation proves the development BTE aggregate at 17 relationships and 91 coverage, but this does not replace the original independent validation owner's package-local red manifest/freeze or authorize L0B. Keep UI independent and production unauthorized.

Owned artifacts: `ART-DSV2-FPR02-BACKEND-DECISION`, `ART-DSV2-FPR02-BTE-PLAN`, `ART-DSV2-FPR02-IOLM-CONSUMER`, `ART-DSV2-FPR02-BODY-WAR-CONSUMER`, `ART-DSV2-FPR02-INTEGRATED-MANIFEST`, `ART-DSV2-FPR02-INTEGRATED-REFRESH`, `ART-DSV2-FPR02-BTE-L0A-EXECUTION-RECEIPT`, `ART-DSV2-FPR02-BTE-L0A-CONTINUATION-HANDOFF`, `ART-DSV2-FPR02-BTE-L0A-PUBLICATION-RECEIPT`, `ART-DSV2-FPR02-BTE-L0A-RECONCILIATION`, `ART-DSV2-FPR02-BTE-L0A-REPAIR-RECEIPT`, `ART-DSV2-FPR02-BTE-L0A-REPAIR-SYNC`

### `CTX-DSV2-FPR02-UI` — FPR-02U required UI development lane

The development work-pack is closed through SWU-UIP-007 and aggregate validation passes. Route its exact authority deltas to DS-D1, DS-D8, supported-profile, and R2 owners. Backend profile decisions and backend release completion are not dependencies; canonical activation remains owner-gated.

Owned artifacts: `ART-DSV2-FPR02-UI-PLAN`

### `CTX-DSV2-FPR02B-CONSUMER-PROOF` — FPR-02B integrated engine and consumer proof

The selected historical L0A implementation and bounded exact-byte repair both pass; current proof is green and no SWU is selectable. Obtain a matching independent red-manifest freeze, then run a later Invoke Refresh before exposing L0B. Consumers remain unchanged until the shared BTE core passes.

Owned artifacts: `ART-DSV2-FPR02-BTE-PLAN`, `ART-DSV2-FPR02-IOLM-CONSUMER`, `ART-DSV2-FPR02-BODY-WAR-CONSUMER`, `ART-DSV2-FPR02-INTEGRATED-MANIFEST`, `ART-DSV2-FPR02-INTEGRATED-REFRESH`, `ART-DSV2-FPR02-BTE-SWU001-CONTEXT`, `ART-DSV2-FPR02-BTE-SWU001-BLOCK-RECEIPT`, `ART-DSV2-FPR02-BTE-L0A-EXECUTION-RECEIPT`, `ART-DSV2-FPR02-BTE-L0A-CONTINUATION-HANDOFF`, `ART-DSV2-FPR02-BTE-L0A-PUBLICATION-RECEIPT`, `ART-DSV2-FPR02-BTE-L0A-RECONCILIATION`, `ART-DSV2-FPR02-BTE-L0A-REPAIR-RECEIPT`, `ART-DSV2-FPR02-BTE-L0A-REPAIR-SYNC`

### `CTX-DSV2-FPR-VISIBILITY` — First-production-release visibility and generated roadmap

After any authorized Craft or FPR manifest update, run the visibility roadmap builder documented in development/first-production-release/visibility/PLAN-TRANSPORT.md, then run the same command with `--check`. Route new material frontiers through the existing persistent research protocol; do not select or advance either FPR-02B or FPR-02U here.

Owned artifacts: `ART-DSV2-FPR-VISIBILITY-PLAN`, `ART-DSV2-FPR-VISIBILITY-BUILDER`, `ART-DSV2-FPR-VISIBILITY-DATA`, `ART-DSV2-FPR-VISIBILITY-HTML`

### `CTX-DSV2-RMT` — Remaining meta-types (WP-RMT-002R reconciliation closed)

WP-RMT-002R reconciliation is closed: RMT2R-OP-001 through RMT2R-TERMINAL-001 passed and the terminal receipt SHA-256 7eddff91e867ed6136483dc5ff5dc91a55699897583667aa1f9525668fddbc73 closes 8/8 receipt-only units. The original 70 WP-RMT-002 Task Session units remain not executed. No immediate continuation is selected. Any admission, registration, ontology, relation materialization, promotion, publication, release, deployment or production work requires a separate governed scope and authorization.

Owned artifacts: `ART-DSV2-RMT001-TERMINAL`, `ART-DSV2-RMT002-PROTOTYPE-VALIDATION`, `ART-DSV2-RMT002R-WORK-PACK`, `ART-DSV2-RMT002R-TERMINAL`

### `CTX-DSV2-SFC` — Stable foundation CLI (WP-SFC-001) — Lane B of the 2026-08-16 owner selection

The 2026-08-21 source-binding refresh passes: all 12 Work Pack bindings are current and SWU-SFC-001 is the nearest selectable unit, but selected_unit remains null. The live registry now contains complete-backend-criteria@2 as a candidate with 13 kinds, 17 relationship IDs and a 26-case corpus, so the historical profile-absent blocker is resolved. It is still not release-admitted, and SFC's SF-02 plus nine projections remain stale at 16 relations and a mismatched profile identity/layout. Next: owner re-ratification and Invoke Refresh to 17/17, exact profile binding/admission, and split SWU-SFC-004 before crossing its positive profile case. No CLI implementation, release, or production readiness is established.

Owned artifacts: `ART-DSV2-SFC-AUTHORING-RECEIPT`, `ART-DSV2-SFC-EXECUTION-ENTRY`, `ART-DSV2-SFC-WORK-PACK`, `ART-DSV2-SFC-INTEGRATION-VALIDATION`

### `CTX-DSV2-STABILITY-REVIEW` — Production-stability baseline review (2026-08-14)

Closed 2026-08-16 with review_result ACCEPT and product_stability_verdict "No current production-stable DomainSpec v2 artifact is established". Its candidate shortlist fed the 2026-08-16 owner selection and Lane B. Nothing further is owed here; the named next human action was executed as DEC-DSV2-FIRST-STABLE-FOUNDATION. The Inventory hook remains deferred.

Owned artifacts: `ART-DSV2-STABILITY-REVIEW-CLOSEOUT`, `ART-DSV2-STABILITY-REVIEW-FINDINGS`

### `CTX-DSV2-ONTOLOGY-FORMS` — Ontology form decisions (all-meta-type architecture/language form campaign)

The historical queue remains 0 ready / 13 blocked, but it no longer controls baseline v2. The owner froze and admitted the exact current 13-type/39-row implementation after canonical definitions and ontology; those form rows are not reopened. Any future semantic or implementation change must create a new versioned baseline.

Owned artifacts: `ART-DSV2-FORM-DECISION-MATRIX`, `ART-DSV2-FORM-IMPLEMENTATION-QUEUE`, `ART-DSV2-META-TYPE-BASELINE-DECISION`, `ART-DSV2-META-TYPE-BASELINE`

### `CTX-DSV2-SICL` — System-integration contract layer (SIC-FAC-000)

SIC-FAC-000-R2 revalidation-B closed PASS 2026-08-13 with zero blockers; the retained 14-file generic-factory candidate satisfies its declared validation surface. The returned route is an Invoke Refresh over "factory-adapted system-integration Revision 2" with executed=false and authorization_included=false. Next is an authorized Invoke Refresh; nothing selects or implements a system-integration target until then. See BLK-DSV2-SICL-REV2-REFRESH.

Owned artifacts: `ART-DSV2-SICL-REPAIR-B-RESULT`, `ART-DSV2-SICL-GOVERNANCE-SIDECAR`

### `CTX-DSV2-SMO` — Shared meta-obligation product readiness (WP-SMO-001)

Refine result is proposal-ready: 325 type/family cells, 31 typed relationship signatures, a 17-SWU plan passing Design/Plan validation and the 35-case receipt-store corpus, readiness attempt 011 returning PLAN_SEMANTIC_READY. The one-shot Task Session returned BLOCK before execution on fingerprint WP-SMO-001:LIVE-ARCANUM-BINDING-AND-ADMISSION-MISSING. The owner selected refresh-after-arcanum-stabilizes on 2026-08-16. Next owner is refine:evidence-refresh once the Arcanum snapshot is stable — not Task Session. Eight residual gates remain (independent critic, renewed G0, attempt-specific G1, G2 applied-corpus audit, runtime/profile locks, G3 readiness, Task Session admission, release authorization).

Owned artifacts: `ART-DSV2-SMO-REFINE-RESULT`, `ART-DSV2-SMO-ONE-SHOT-BLOCK`, `ART-DSV2-SMO-G1-REPAIR-RECEIPT`

### `CTX-DSV2-FMP` — Formal-model proof provider (WP-FMP-001, finite TLA/TLC evidence)

Refine closed PASS 2026-08-16: the planning package is complete and selection-ready with eight ordered SWUs, 41 frozen target baselines, 24 source/tool locks, 35 hostile cases, and two exact corpora (Bolina; the order-fulfillment corpus, with FreshnessSafety deliberately preserved as known-red). Execution entry is selection-ready with next owner implementation-readiness:execute. Zig-to-TLA conformance is deliberately excluded as the typed future WP-FMP-TRACE-001 (GAP-DSV2-FMP-TRACE).

Owned artifacts: `ART-DSV2-FMP-RESULT`, `ART-DSV2-FMP-WORK-PACK`

### `CTX-DSV2-IMPL-CONFORMANCE` — Implementation conformance (profile-bound composition and normalization layer)

The frozen baseline removes the recurring per-type/profile prerequisite. Candidate-3 closes `SWU-MTCLI-002` with the bounded instantiate contract and 17/17 focused tests. The first-class enforcement registry separates open evidence repairs, target findings and the eight missing machinery capabilities. `SWU-MTCLI-003` is selectable but not selected; no later unit is implicit.

Owned artifacts: `ART-DSV2-IMPL-CONFORMANCE-DEFINE`, `ART-DSV2-IMPL-CONFORMANCE-ARCH`, `ART-DSV2-META-TYPE-CLI-PLAN`

### `CTX-DSV2-EVF` — Evolvable validation framework

L0/L1 and the bounded L2 reachability slice remain passing evidence. The 17-relationship BTE proof-engine reconciliation, S1 exact-ref repair, and the 49-finding format-honesty baseline each pass their authorized local scopes. The 53-path runtime-repair candidate now has exact 3-of-3 owner acceptance, opening only its bounded submodule-first publication edge; publication has not been performed here. Original BTE/IOLM owner prerequisites, proposal acceptance, canonical apply, independent readiness, fresh retry authorization and selection remain closed. Next: decide whether to exercise the exact accepted publication edge, then collect the retained owner/readiness receipts before any new P0 run. Separately, the optional SMT verify/witness continuation is an EVF provider-integration gap: define and admit a pinned, fail-closed provider contract before execution; the TDE tower remains source evidence for the decidability boundary. No U1 selection, SMT-provider admission, release, or production claim.

Owned artifacts: `ART-DSV2-EVF-WORK-PACK`, `ART-DSV2-EVF-ONE-SHOT-READINESS`, `ART-DSV2-EVF-L2-PROTOTYPE`, `ART-DSV2-EVF-L2-CLOSURE`

### `CTX-DSV2-MTF` — Legacy meta-type factory reproducibility

This legacy MTF lane has MTF-001..MTF-029 complete with an empty remaining set and authority_effect none. The 2026-08-07 reproducibility prototype passed: two isolated runs produced the same semantic receipt over a nine-node locked graph with an unchanged product-tree inventory. Claim ceiling is same-host local reproducibility — not cross-host provisioning, ontology promotion, implementation authority, release, or production readiness. `CTX-DSV2-REALIZATION-KERNEL` separately owns the newer 13-family/39-row implementation frontier.

Owned artifacts: `ART-DSV2-MTF-EXECUTION-STATE`, `ART-DSV2-MTF-REPRODUCIBILITY`

### `CTX-DSV2-REALIZATION-KERNEL` — Current meta-type realization kernel and families

The exact current implementation evidence is frozen and owner-admitted as `domainspec-meta-types-current-implemented@2` at baseline digest `10c29c2a4feb5039b6c90dcd7e2d44024757b4dd2414f9c0383c82387ec6e836`. Its 771-file inventory includes canonical definition bytes, all 39 selected realization rows and the supporting family, kernel, factory and acceptance evidence. The current-state JSON and ontology projection bind this exact manifest. Next is consumption by `WP-MTCLI-001`; changing any frozen byte requires a new baseline version. Generated-target conformance, publication, release, deployment and production remain unproven.

Owned artifacts: `ART-DSV2-REALIZATION-KERNEL-FAMILIES`, `ART-DSV2-META-TYPE-BASELINE`

### `CTX-DSV2-FORMAT-HONESTY` — Format honesty and generated meta-type cards (WP-FMT-001)

SWU-FMT-001 executed PASS: the dependency-free checker and seven tests pass and the governed project surface reports exactly 49 json-content-yaml-name violations. Its Task Session closeout is NOT-RUN; SWU-FMT-002 is therefore not eligible. Next: invoke:refresh:apply-approved over the six declared closeout targets, then select at most SWU-FMT-002 through a fresh route. The result does not rename files, repair the 49 findings or card-edge drift, close the permanent Refine admission defect, or authorize promotion, publication, or release.

Owned artifacts: `ART-DSV2-FMT-WORK-PACK`, `ART-DSV2-FMT-EXECUTION-ENTRY`, `ART-DSV2-FMT-SIDECAR`, `ART-DSV2-FMT-CHAIN-RECORD`, `ART-DSV2-FMT-REFINE-RESULT`

### `CTX-DSV2-BMC` — Backend meta-type conformance (WP-BMC-001)

BMC-EVD-001 is a historical FLAG snapshot with 30 binding findings: three stale Value Object bindings and nine absent Enum plus six absent bindings each for Query, Calculation and Policy. Later Rule source/provider changes add six live digest drifts against that snapshot. All 13 types still have three realization rows, but every queue-ready value is false and ontology admission remains not-admitted. Refresh the maturity snapshot without hiding the current Operation and Workflow evaluator findings. CTX-DSV2-BMC-REL is no longer blocked at N05: N05 is owner-selected, the nonnumeric continuation reached N45, and the nine-file EVF candidate passed staging and candidate-local review. Its governance repair passed, but post-repair independent review, two-run real closure, frozen graph and independent graph review remain missing. After evidence readiness and BMC-REL admission, BMC-OBS-001 is the first product candidate: a shared TypeScript syntax/symbol evidence kernel. No product mutation, profile admission, ontology change, promotion, or release is authorized by the evidence receipt.

Owned artifacts: `ART-DSV2-BMC-REFINE-RESULT`, `ART-DSV2-BMC-EVD-RECEIPT`, `ART-DSV2-BMC-MATURITY-MATRIX`

### `CTX-DSV2-BMC-REL` — Relationship constraint owner decisions (BMC-REL-001)

N05 is closed with owner-selected uniform cycle-policy governance, and the nonnumeric design continuation has progressed through N45. The nine-file EVF candidate passed staging and candidate-local review; the selected opaque-text governance repair also passed. Obtain post-repair independent review, run real nine-target closure twice, freeze the closure graph, and obtain independent graph review before evaluating owner-request eligibility. The 31-row packet remains unaccepted; canonical apply and implementation are not authorized.

Owned artifacts: `ART-DSV2-BMC-REL-PACKET`, `ART-DSV2-BMC-REL-DESIGN-RESULT`, `ART-DSV2-BMC-REL-N05-SELECTION`, `ART-DSV2-BMC-REL-N45-CLOSEOUT`, `ART-DSV2-BMC-REL-EVF-CANDIDATE-STAGING`, `ART-DSV2-BMC-REL-CANDIDATE-REVIEW`, `ART-DSV2-BMC-REL-PREACCEPTANCE-DEFECT`, `ART-DSV2-BMC-REL-GOV-REPAIR-SELECTION`, `ART-DSV2-BMC-REL-GOV-REPAIR-APPLY`, `ART-DSV2-BMC-REL-CRAFT-FRONTIER-BINDING`, `ART-DSV2-BMC-REL-CRAFT-FRONTIER-VALIDATOR`

### `CTX-DSV2-PROOF-OBLIGATION-SUBSTRATE` — Proof-obligation cross-boundary substrate

DomainSpec v2 owner acceptance is recorded over the exact replacement candidate digest c9e072b557ded19996be9e44a8f7f983021083471425bf2fcdd14a084a598498. The candidate file's own pending prose is historical pre-acceptance text; the separate acceptance receipt controls current state. Next: refresh GATE-01 so it binds this accepted DomainSpec v2 candidate and retires the old v1 route. Until then there is no proof discharge, evaluator validation, promotion, publication, or authority transfer.

Owned artifacts: `ART-DSV2-PROOF-SYNTAX-CANDIDATE`, `ART-DSV2-PROOF-SYNTAX-ACCEPTANCE`

### `CTX-DSV2-ORODI` — Operational resilience, observability and deployment integration

Exact live subject and environment binding is deferred by owner decision. ORODI remains a non-executing Plan with zero mutation-capable units. Product implementation cannot start from this Work Pack. To build code without live bindings, explicitly authorize a separately scoped candidate-local prototype lane with an exact target, Work Pack, write scopes and validation contracts; otherwise resume the deferred owner/profile binding route. No Task Session, infrastructure effect, canary, deployment, rollback, promotion or release route is exposed.

Stage/gate: `plan` / `block`. Invoke Define and Design pass; the complete Plan remains `flag` because it is non-executing. The Wave-0 coordinator is bound, while live subject/environment binding is explicitly deferred and all field-level owner/admission bindings remain absent.

Pending: `BLK-DSV2-ORODI-LIVE-BINDINGS`; `GAP-DSV2-ORODI-TOOL-PROFILE-ADMISSION`; deferred live subject/environment binding, field-owner bindings, lifecycle-owned admissions, and any separately authorized prototype or later Invoke Refresh route.

Owned artifacts: `ART-DSV2-ORODI-RESEARCH`, `ART-DSV2-ORODI-INVOKE-DEFINE`, `ART-DSV2-ORODI-INVOKE-DESIGN`, `ART-DSV2-ORODI-INVOKE-PLAN`, `ART-DSV2-ORODI-OWNER-BINDING-DECISION`

## Decisions

### `DEC-FPR01-002-ADOPTION-ACTIVATION` — `closed`

How should the approved FPR01-002 owner-disposition packet be activated and adopted? Selected/default: `combined-narrow-activation`. The user selected combined narrow activation and unchanged packet adoption on 2026-07-16. Fail-closed validation reopens only the affected owner queue if a packet check fails.

### `DEC-DSV2-FPR-W0-PROOF-SYNC` — `closed`

How should foundation execution continue after the accepted 007 retry receipt proves the current guard? Selected/default: `synchronize-w0-proof-only`. The user selected Option 1 on 2026-07-14. A proof-only synchronization preserves the one-SWU boundary and prevents a completed receipt from being mistaken for permission to execute the L1 census.

### `DEC-DSV2-FPR-SGRM007-ACTIVATION` — `closed`

How should foundation execution continue after the accepted SGRM-006 retry review exposed stale selection controls? Selected/default: `refresh-and-execute-sgrm-007-r1`. The user selected Option 1 on 2026-07-14. Refreshing live selection controls before implementation preserves the declared Craft/work-pack authority order and keeps the red guard visible until a new receipt passes.

### `DEC-DSV2-CRAFT-SCOPE` — `closed`

Should DomainSpec v2 have its own Craft space, or stay one context in the cav2 ledger? Selected/default: `own-scoped-craft`. v2 outgrew a single cav2 row — it has multiple nested sub-contexts (authority / make-it-green / reformulate-batch1 / spec-ontology) each with its own blockers, decisions, gaps, and recomposition. A scoped .craft/ is not a new cav2 folder (memory constraint intact); cav2 stays umbrella + points here.

### `DEC-DSV2-LANE-ZA` — `closed`

Lane Z (fuse spec == ontology) vs Lane A (keep separate + generated bidirectional mapping)? Selected/default: `one-semantic-graph-owned-branches`. Superseded and resolved by DEC-DSV2-SPEC-ONTOLOGY-ARCHITECTURE-001 on 2026-08-23. The selected architecture uses one connected semantic graph while retaining separately owned branches and generated non-authority projections; it is neither the old full-fusion shorthand nor a permanently separate mapping pair.

### `DEC-DSV2-EDGE-ADMISSIBILITY` — `closed`

What governs whether a RELATIONSHIPS edge earns its own type, vs folding into a node type or a coupling flag? Selected/default: `build-from-owned-cav2-orthogonality`. The edge-law admissibility test ("an edge earns its type iff it composes into different code") is a domain specialization of owned cav2 invariants — CAV2-D22 (orthogonal classification), CAV2-D29 (axis orthogonality), CAV2-D16 (typed coupling). Rulings: keep enforces vs applies (guard vs select); collapse enforces/enforces-cross to one edge + a cross-feature flag; reject queries for Calculation->Policy (redundant with applies); widen applies to Policy->{Operation, Calculation}. Scope = governance orthogonality, NOT Lean/Hilbert projector orthogonality (excluded from cav2).

### `DEC-DSV2-APE-L0-DOMAIN` — `closed`

Which domain should the L0 POC feature pack use to make the node-plane validators non-vacuous? Selected/default: `reuse-the-spec-ontology-toy-domain`. Owner chose (decision-gate, 2026-07-02) to REUSE the owned financial-settlement domain — the spec-ontology toy's corpus — rather than author a new one. Build-from-owned: backend aspect files already exist under impl/test-derivation-engine/__fixtures__/financial-settlement/ and were typed into 23 nodes by the toy's T1 graph extraction; it is node-rich (good for node-plane L0), engine lint/roundtrip can target it, and it connects L0 to the SURVIVED-narrow evidence. The default (author-new) was demoted once grounding showed an owned real domain exists; the sample stub is empty (zero concepts) so promote-sample collapsed into author-new and was folded out.

### `DEC-DSV2-SPEC-HOMING` — `closed`

Should all impl/spec/*.md governance docs be removed and consumed from root definitions/? Selected/default: `no-hand-projections-route-to-owner`. Dialectic 2026-07-06. Thesis: single authority removes the projection-drift failure mode behind the R3A orphan. Antithesis: the two-plane boundary (DEF-DSV2-TWO-PLANE) is deliberate; 4 of 6 docs are prose with no consumer; forcing AXIOMS into definitions/ violates the project's own orthogonality rule (domainspec-v2-D3/CAV2-D22 — a proposition is not a term). Synthesis: the real invariant is "no HAND-authored projections", not "no projections" — any impl/spec view is generated from root and CI-verified, or deleted. Per-doc: RELATIONSHIPS delete+consume-root; TAXONOMY migrate UI-11 to root then delete/generate; CONSTITUTION -> authority/constitutions (R6a/R6b); AXIOMS -> authority/ (basis) not definitions/; DRIFT -> drift-governance owner; TEST-PIPELINE STAYS contract-plane.

### `DEC-B1-SATURN-AXIOM-SCOPE` — `closed`

Which v1 axioms/constitution rules belong in DomainSpec-v2 vs the Saturn (loop) pillar? Selected/default: `scope-down-to-saturn`. Owner decision via decision-gate 2026-07-06 (recommended option). Three-pillar model: Saturn owns the observability/reflection loop. Per-rule cut — STAY in DomainSpec-v2: A1 (semantic authority), A2 (adapter line), A3 (RECAST: governance methods must be runnable/computable); C1 (spec=source-of-truth / base), C2 (no domain logic in adapters / layering), C5 (critical violations block merge / validation-shift-left), C6 (code<->concept anchors / layering), C7 (alignment+layering audits / layering-drift), C8 (deterministic detectors / validation — underpins the engine). ROUTE to Saturn (DROP-with-pointer): A4 (observer/executor), A6 (feedback budget); C3 (signal schema), C4 (dual observer), C9 (telemetry), C11 (metrics/reflect). STRADDLERS (R6a resolves with this default): A5 — keep the shift-left half (realized as C5), route the reflection-outer-loop half to Saturn; C10 (prune-by-evidence / via-negativa) — keep as DomainSpec drift governance; its feedback-budget cadence references Saturn A6.

### `DEC-DSV2-FIRST-STABLE-FOUNDATION` — `closed`

What is the first stable-foundation hardening target for DomainSpec v2, and what exactly is selected across artifact form, profile breadth, conformance claim, runtime boundary, distribution, diagnostics, compatibility, security, resource and retention? Selected/default: `harden-cli-foundation-first`. Harden a private, pre-production CLI foundation first (SF-01/A) while the remaining meta-type planning lane continues separately. Bound to feature-with-independent-node-and-edge-files@1 (SF-02/P2: 13 active backend meta-types, 16 backend relationship signatures, project-level cross-feature edges), claiming exact-profile causal implementation conformance (SF-03/C2), with an atomic state-plus-outbox durable-fact boundary (SF-04/S1), compiled JavaScript on one pinned external Node v24.19.0 on Linux x64 (SF-05/A1, SF-06/E1), npm 11.17.0 with one root lockfile (SF-07/M1), separate structural-receipt and diagnostic-report schemas (SF-09/D1), stdout results / stderr faults (SF-10/O1), a fixed exit-code taxonomy (SF-11/EC1), command name domainspec-v2 (SF-12/B1), private repository-local distribution (SF-13/RC1), package identity @domainspec-v2/cli (SF-14/PK1), internal-confidential pointer-only diagnostics (SF-15/SEC1), explicit project root only (SF-16/IR1), stated admission and resource limits (SF-17/L2), deny-by-default lifecycle scripts (SF-18/BS2), paginated deterministic lint output (SF-19/OUT2), conditional immutable rollback (SF-20/RB1), and permanent acceptance-bound retention (SF-21/RET1).

### `DEC-DSV2-SPEC-ONTOLOGY-ARCHITECTURE-001` — `closed`

What top-level architecture connects business meaning, formal claims, proof obligations and system evidence? Selected/default: `one-semantic-graph-owned-branches`. Direct user selection A recorded in the architecture decision on 2026-08-23.

### `DEC-DSV2-BMC-REL-N05` — `closed`

Should future same-dimension longer-cycle policy be uniform across D29 dimensions or governed per dimension? Selected: `uniform-future-rule`. Exact user response A was recorded on 2026-08-23 and bound to `BMC-REL-NONNUMERIC-05-A-UNIFORM-CYCLE-POLICY-ACROSS-DIMENSIONS`. This selects governance topology only; it does not authorize packet mutation or implementation.

### `DEC-DSV2-ORODI-OWNER-BINDING-AUTHORITY` — `closed`

Who should coordinate Wave 0 while every field remains separately accepted by its own owner? Selected: `ORODI-COORD-INITIATING-OWNER`. Vlad Rondelli, acting as initiating DomainSpec v2 project owner, explicitly accepted the limited Wave-0 coordinator role; no additional rationale was supplied. Vlad owns packet integrity, field inventory, routing and completeness only; the decision does not assign or satisfy any semantic, profile, evaluator, evidence, infrastructure, deployment, promotion or release field-owner gate.

### `DEC-DSV2-ORODI-LIVE-TARGET-DEFER` — `closed`

Should exact live subject and environment binding be completed now or deferred? Selected: `defer-live-target-binding`. The user explicitly deferred those fields on 2026-08-24. The deferral does not waive `BLK-DSV2-ORODI-LIVE-BINDINGS`, create a mutation-capable unit, expose Task Session, or authorize implementation, infrastructure, deployment, promotion or release.

### `DEC-DSV2-META-TYPE-BASELINE` — `closed`

Which existing meta-type implementation evidence becomes the fixed starting point for external-project CLI instantiation? Selected: `freeze-current-implemented-evidence`. This historical decision admitted `domainspec-meta-types-current-implemented@1`; it remains immutable history but is superseded as the current CLI baseline because canonical definitions and ontology did not precede its freeze.

### `DEC-DSV2-META-TYPE-CANONICAL-DOCS-BASELINE-V2` — `closed`

What must become canonical before the implemented meta-type baseline is frozen for CLI consumption? Selected: `definitions-and-ontology-first-then-freeze-v2`. The owner directly required the definitions and DomainSpec v2 ontology to express the current state first. D31-D35, the schema-validated current-state pointer and the ontology/projection now bind `domainspec-meta-types-current-implemented@2`; baseline `@1` remains historical. No product unit, publication, release, deployment or production effect follows.

## Active blockers

### `BLK-DSV2-DRIFT-ENGINE`

Drift governance is designed but not implemented in the engine (Stream<CheckResult> + guardedness).

Owner route: `none`. Closure: An engine realization of the drift stream + guardedness type exists and DRIFT-CONVERGENCE.md's 5 surfaces bind to runnable methods (R-trend-type residue closed).

### `BLK-DSV2-L2-ATTESTATION`

L1 integrity sealing passed for SWU-R3C-010; the external L2 actor-identity signature for the 3 ratified governance kinds remains unavailable.

Owner route: `none`. Closure: An external actor-identity and key-custody model is decided, the sealed tuple is signed, and a third-party-runnable verifier proves valid, bad-signature, and unknown-actor outcomes.

### `BLK-DSV2-SMO-ARCANUM-BINDING`

WP-SMO-001 one-shot execution returned BLOCK before Context Builder. The live Arcanum repository binding is stale, the Cedar, Souffle and idempotency-retention runtime locks are absent, no stable applied Work Pack exists, and there is no SWU selection or single-use mutation admission.

Owner route: `refine:evidence-refresh (not task-session)`. Closure: A stable Arcanum snapshot exists, a refine:evidence-refresh produces fresh inventory, readiness audit and critic receipts, the three runtime/profile locks are present, and renewed G0 owner acceptance plus an attempt-specific G1 authorization are recorded before any Task Session admission.

### `BLK-DSV2-SICL-REV2-REFRESH`

SIC-FAC-000-R2 revalidation-B passed with zero blockers, but its returned Invoke Refresh route over the factory-adapted system-integration Revision 2 is recorded as executed=false with authorization_included=false. The revalidated candidate therefore cannot advance.

Owner route: `invoke refresh with explicit authorization`. Closure: An authorized Invoke Refresh executes over Revision 2 and returns a receipt that accepts or explicitly rejects the retained 14-file generic-factory candidate.

### `BLK-DSV2-P2-DENOMINATOR-DRIFT`

The accepted 2026-07-17 FPR-02 decision selected "all 16 backend signatures admitted and exercised" and was correct when made — at that commit relationships.yml held 30 signatures, 16 backend-scoped. Commit 82edd13e4 on 2026-07-23 added the `creates` signature (Operation -> Entity, same-feature), moving the backend denominator to 17. The invalidation trigger that SPEC.md line 57 declares for a changed relationship binding did not fire. The stale 16 propagated into SF-02 on 2026-08-16 and into nine WP-SFC-001 artifacts including the SWU-SFC-004 acceptance boundary, while WP-SMO-001 independently recorded the correct 17 on 2026-08-14.

Owner route: `profile owner re-ratification, then invoke refresh over the Lane B package`. Closure: The owner re-ratifies the 16/16 quantity as 17/17 with its admitted-and-exercised obligation, `creates` obtains positive corpus coverage and negative controls, the nine projection sites listed in ART-DSV2-P2-COUNT-PATCH are corrected through an Invoke Refresh with exact owner approval, and the two-lane integration check is re-run with a denominator-agreement assertion added so this class of divergence fails closed. Past validation records are superseded by re-run, not retroactively edited.

### `BLK-DSV2-REFINE-PLAN-ADMISSIBILITY`

The refine sigil can synthesize a pass result around an Invoke Plan output that its own recommended next owner cannot admit. WP-FMT-001's first plan was prose only: zero write-scope declarations across 14 units and all six closeout-contract fields absent. The refine run reported pass and recommended task-session; task-session-until-blocker returned BLOCK at preflight on preconditions 3 and 4. The nine refine dispatch gates covered stage receipts, owner boundary, digest completeness, comment preservation, in-flight collision and the Craft contract, but none asserted that a plan is admissible by its declared next owner.

Owner route: `sigil-development on refine`. Closure: The refine sigil gains gate G-plan-admissible: when Invoke Plan names an execution-capable next owner, the run must not synthesize pass until the plan output satisfies that owner's documented admission preconditions, or records an explicit blocked reason naming them. The instance defect for WP-FMT-001 is already repaired by ART-DSV2-FMT-SIDECAR; this blocker tracks the permanent fix only.

### `BLK-DSV2-SPEC-ONTOLOGY-VERIFIER-ADMISSION`

The @4 contract package is candidate-valid and Rondelli's aggregate selection is recorded, but all eleven owner slices remain verification-pending. Victor Boscaro has not authenticated, accepted the V1 policy or issued the required V1/V2 receipts, so protected roles cannot be admitted.

Owner route: `Victor verifier response plus exact structural verification`. Closure: Victor directly accepts the exact unchanged @4 identity/role/policy contract, required V2 receipts and exact V1 checker receipts validate, and only then are the eleven separate owner responses materialized and admitted at their own scope ceilings.

### `BLK-DSV2-BMC-REL-PREACCEPTANCE-CLOSURE`

The nine-target EVF candidate and its candidate-local review pass, and the selected opaque-text governance repair was applied with its focused and full tests passing. Preacceptance remains blocked because no post-repair independent review, two-run real nine-target closure, frozen closure graph, or independent closure-graph review is recorded.

Owner route: `invoke preacceptance owner plus independent reviewer`. Closure: bind an independent review to the exact applied governance repair, run the real nine-target closure twice with byte-identical outputs, freeze one immutable closure graph, and obtain an independent graph review. Only then may request eligibility be evaluated.

### `BLK-DSV2-PROOF-GATE01-BINDING`

The DomainSpec v2 replacement candidate is owner-accepted, but the earlier GATE-01 ratification still binds the superseded v1 candidate and receipt.

Owner route: `refreshed GATE-01 owner decision`. Closure: A refreshed GATE-01 decision binds the exact accepted DomainSpec v2 candidate, authority-model and syntax digests and retires the old v1 route without transferring meaning or lifecycle authority.

### `BLK-DSV2-EVF-P0-EXECUTION-ADMISSION`

Runtime-repair acceptance opens only an exact 53-path publication edge. Original BTE/IOLM prerequisites, proposal acceptance, canonical apply, independent readiness, fresh retry authorization, dispatch registration and unit selection remain closed.

Owner route: `retained owner gates then implementation-readiness`. Closure: Complete the separately owned prerequisite and readiness receipts, preserve any bounded publication as a distinct edge, obtain a fresh run ID and explicit retry authorization, and select at most one eligible unit.

### `BLK-DSV2-ORODI-LIVE-BINDINGS`

No exact live subject, environment, accountable owners, technology profiles, tools, evaluators, policy, evidence expiry, infrastructure target or deployment authority is bound.

Live subject and environment binding is explicitly deferred by `DEC-DSV2-ORODI-LIVE-TARGET-DEFER`; that decision does not waive or close this blocker.

Owner route: `owner decisions and profile admission, then invoke:refresh`. Closure: separate owners accept exact bindings; ontology/profile admission validates; a later Invoke Refresh materializes only accepted deltas.

## Active gaps

### `GAP-SH-UI11-MIGRATE` — `medium`

The 11 UI meta-types are enumerated only in impl/spec/TAXONOMY.md (root definitions/meta-types/meta-types.yml is backend-14). Per DEC-DSV2-SPEC-HOMING, TAXONOMY.md must NOT be deleted (R2) until the 11 UI types are migrated to the root meta-type authority, else they orphan.

Treatment/owner: `migrate-content-before-delete` / `batch-1 R2 / meta-type-definitions MT5`.

### `GAP-SH-PROSE-HOMES` — `medium`

DRIFT-CONVERGENCE.md still has no owner-surface home yet (drift-governance for DRIFT). The AXIOMS/R1 half was resolved 2026-07-10 by authority/AXIOMS.{md,yml} plus CAV2 definition-sync, and impl/spec/AXIOMS.md is absent/non-authority. Per DEC-DSV2-SPEC-HOMING the DRIFT projection must NOT be deleted (R5) until its owner-surface home exists, else the prose content orphans.

Treatment/owner: `author-owner-home-before-delete (R5 remaining; R1 fixed-in-R1A)` / `batch-1 R5 + constitution-governance`.

### `FR-FPR-ONTOLOGY-DIRECTION` — `block`

Reconcile the active contract-to-authoring ontology lens with the accepted governed business-plane-to-Spec chain. Candidate ontology projections have no authority effect; an owner decision must define direction, supersession, provenance, and contradiction handling before FPR-03 can promote B-to-Spec mappings.

Treatment/owner: `plan` / `semantic owner + definitions-governance`.

### `FR-FPR-SOLVER-PROFILE` — `block`

Select literal formal languages, translator versions, solver executables/versions, relational and state bounds, timeout/resource ceilings, result taxonomy, and fairness/liveness policy. Research receipts are upstream evidence only; FPR-06 remains blocked until the profile is promoted and reproducible.

Treatment/owner: `plan` / `formal-validation owner + semantic owner`.

### `FR-FPR-BW-ORIGIN-ROUTE` — `block`

Decide whether the Body War witness requires a real provider and bind callback, deployment, origin, consent, CSRF, and allowed-redaction fields. A fake-only route requires explicit claim narrowing and cannot silently satisfy the accepted end-to-end profile.

Treatment/owner: `plan` / `Body War product/security owners + DomainSpec claim owner`.

### `FR-FPR-I-ROOT-DISPOSITIONS` — `block`

Ratify the complete Body War production, test, generated, static-JS, and non-code root set plus pinned parser/tool semantics. Missing roots, unresolved symbols, comment/dead-only text, and unanalyzed dynamic behavior must fail or remain indeterminate; tags alone do not establish structure.

Treatment/owner: `plan` / `implementation/platform owner`.

### `FR-FPR-APE-SELF-CONTAINMENT` — `block`

Prove the first-release architecture and composition catalogs are self-contained in v2. If any runtime or proof path still depends on private v1 method material, promote the shared-method package as a real FPR-05 dependency instead of treating it as deferred general hardening.

Treatment/owner: `plan` / `layering governance + runtime owner`.

### `GAP-DSV2-SFC-UNEXECUTED` — `block`

WP-SFC-001 is authored and selection-ready with 20 SWUs, but selected_unit is null, all 20 planned validation contracts are unexecuted, and prerequisites SFC-PR-001..SFC-PR-004 remain open at their owning units. No CLI byte exists; the planning package is not evidence of an artifact.

Treatment/owner: `plan` / `profile/P2 refresh, then implementation-readiness:execute`.

### `GAP-DSV2-FMP-UNSELECTED` — `medium`

WP-FMP-001 is selection-ready with eight ordered SWUs and frozen baselines, but no unit is selected and no TLA/TLC proof has been executed against the live factory. Bounded model adequacy is planned, not obtained.

Treatment/owner: `plan` / `implementation-readiness:execute`.

### `GAP-DSV2-FMP-TRACE` — `medium`

Zig-to-TLA conformance is deliberately held outside WP-FMP-001 as the typed future WP-FMP-TRACE-001. It is blocked on real grant-path instrumentation, exact trace/action bindings, source/projector locks, and unresolved publication/tombstone semantics. Until it exists, model adequacy must not be read as implementation proof.

Treatment/owner: `defer-with-typed-successor` / `formal-validation owner`.

### `GAP-DSV2-TWO-LANE-INTEGRATION` — `block`

Lane A reconciliation is terminal candidate-local pass and Lane B source freshness is current, but the shared profile identity and denominator are still split: the live candidate is 13 kinds/17 relationships while SFC retains a 16-relation selection and mismatched identity/layout. The integration gate must be rerun after exact 17/17 owner re-ratification and SFC refresh; neither planning evidence nor the candidate profile authorizes release.

Treatment/owner: `plan` / `FPR owner + both lane owners`.

### `GAP-DSV2-SFC-004-FUSED` — `medium`

SWU-SFC-004 fuses work that is unblocked with work that is blocked. Seven of its eight acceptance cases are negative controls needing only fixtures, which CROSS-TASK-GAPS.md already permits before an owner receipt exists; exactly one case — the approved binding passes — needs SFC-PR-001. Because CLOSEOUT-CONTRACT.md requires the acceptance-critical command to pass before a unit closes, and closure is what makes the successor eligible, the fused unit stops the chain at unit 4 of 20. Runway as written is three units. Splitting 004 into 004a (schemas, fail-closed readers, seven negative controls) and 004b (the single approved-binding positive) and re-parenting 005/006 onto 004a yields six units of runway. Re-parenting 005 onto 003 is NOT a valid alternative: SPEC.md requires the structural receipt to be source/profile/version-bound, so the receipt schema genuinely needs the profile-binding shape 004 authors.

Treatment/owner: `split-unit-before-selection` / `Lane B plan owner via Invoke Refresh`.

### `GAP-DSV2-CARD-EDGE-DRIFT` — `high`

Measured 2026-08-19 against live definitions/relationships/relationships.yml: 8 of 13 meta-type cards under impl/spec/meta-types/ disagree with the edge authority, and 3 assert relationships that do not exist. calculation.md claims SOURCE of `derives` (actually View Model to Entity) and TARGET of `performs` (actually Entity to Operation); rule.md claims SOURCE of `applies` (actually Policy to Operation/Calculation); enum.md claims TARGET of `contains`. event.md omits `produces`, one of only three relationships in the sole currently-admitted profile. interface, state-machine, query and mapping cards are incomplete. Root cause is identical to the 16-vs-17 denominator drift found the same day: a derived fact copied by hand and never re-derived.

Treatment/owner: `correct-then-generate` / `WP-FMT-001 layers L1 (SWU-FMT-004/005) then L3`.

### `GAP-DSV2-BMC-REALIZATION-BINDINGS` — `high`

BMC-EVD-001 records 30 binding findings across the TypeScript/Python/Rust realization surface: three stale Value Object bindings and nine absent Enum plus six absent bindings each for Query, Calculation and Policy. Six later Rule source/provider digest changes also make that maturity snapshot stale. Queue readiness remains false.

Treatment/owner: `refresh-bindings` / `BMC evidence owner through implementation-readiness`.

### `GAP-DSV2-FMT-SWU001-CLOSEOUT` — `high`

SWU-FMT-001 execution passes, but closeout_result is NOT-RUN and its six planning/control targets have not been synchronized. SWU-FMT-002 is not eligible until apply-approved closeout succeeds.

Treatment/owner: `closeout-before-successor` / `invoke:refresh:apply-approved`.

### `GAP-DSV2-EVF-SMT-PROVIDER` — `medium`

The SMT/FOL research tower grounds the deterministic derivation engine's decidability and `needs_formal` boundary, but no EVF contract, admitted runtime profile, evaluator binding, or receipt currently integrates an SMT solver for optional verify/witness work. That operational continuation belongs to EVF's evidence chain, while any solver runtime may retain separate provider ownership; it is not a TDE implementation frontier and is not implemented by the existing Souffle/Alloy L2 slice.

Treatment/owner: `defer-with-typed-provider` / `EVF formal-validation owner through a separate define, design, provider-admission and validation route`.

Evidence: [`SMT/FOL source research`](../../research/smt-fol-test-derivation/) · [`TDE provenance ledger`](impl/test-derivation-engine/.craft/ledger.yml).

### `GAP-DSV2-ORODI-TOOL-PROFILE-ADMISSION` — `block`

Researched tool families have no selected or admitted versioned technology profile or portability boundary.

Treatment/owner: `defer` / `technology-profile and deployment-policy owners through decision-gate and Invoke Refresh`.

### `GAP-DSV2-META-TYPE-TARGET-ENFORCEMENT` — `high`

This is product implementation work, not a remaining baseline-governance gate. DomainSpec now has an owner-admitted frozen catalog, but the CLI does not yet decode a target DomainSpec project, select rows from that catalog, deterministically instantiate them, publish atomically, emit a baseline-bound receipt, or observe the target’s real structure, declared reads/writes/effects, guard order, atomic state/outbox behavior, failure continuation and typed relationships.

Treatment/owner: `implement-frozen-catalog-instantiation-and-fail-closed-observation` / `WP-MTCLI-001 under CTX-DSV2-IMPL-CONFORMANCE; select SWU-MTCLI-003 next`.

## Recompositions

- `REC-DSV2-GREEN` — `partial`: G1/G2/G3 recomposed — impl/ green unblocks the reformulation + freeze gate. G4 residue (CI wiring).
- `REC-DSV2-TOY` — `partial`: Toy T1-T4 and later branch-design evidence recomposed into the selected one-semantic-graph architecture. Residue is exact @4 verifier evidence, protected owner admissions, schemas, validators and any separately authorized migration; Lane Z-vs-A selection is no longer open.
- `REC-DSV2-FIRST-PRODUCTION-RELEASE` — `partial`: FPR-01, the stability review, the first-stable-foundation decision, RMT reconciliation and the SFC source refresh are recomposed into the v2 root. FPR-02 backend and UI remain independent. The live P2 candidate is 13 kinds/17 relationships, but SFC still binds stale 16-relation projections and no selected unit exists. Profile admission, full conformance, formal validity, pilot acceptance, release readiness and production authorization remain unestablished.
- `REC-DSV2-FPR02-BACKEND` — `partial`: Backend profile and pilot ownership remains isolated from UI development. Historical L0A and its repair pass, and newer development BTE evidence passes at 17 relationships/91 coverage. The independent validation owner freeze, L0B admission and every release/promotion gate remain open.
- `REC-DSV2-FPR02-UI` — `partial`: The required UI development profile continues in its existing work-pack without blocking the backend first-release lane. SWU-UIP-001..007 and aggregate development validation are complete; exact authority handoffs and canonical activation remain owner-gated.
- `REC-DSV2-FPR-VISIBILITY` — `complete`: The deterministic Craft-backed roadmap read model is planned, generated, browser-validated, and indexed. It improves visibility and continuation without selecting the parent's FPR-02 decision boundary, changing any frontier state, or authorizing production. The Whisper transport remains candidate pending real-use observation.

## Artifact index

- [`ART-DSV2-IMPORT-MANIFEST`](IMPORT-MANIFEST.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-IMPL`](impl/) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-AUTHORITY`](authority/) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-MAKE-IT-GREEN`](development/make-it-green/) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-REFORMULATE-BATCH1`](development/reformulate-batch1/) — `candidate` · `artifact` · owner `unscoped`
- [`ART-DSV2-IMPORT-TRIAGE`](research/2026-06-29-v1-import-triage/findings.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-RECURSION-RESEARCH`](research/2026-06-29-recursive-governance-model/findings.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-SPEC-ONTOLOGY-RESEARCH`](research/2026-07-01-spec-as-ontology/findings.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-SPEC-ONTOLOGY-TOY`](research/spec-ontology-unification/) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-COMPOSABILITY-SYNTHESIS`](research/2026-07-01-composability-edges-taxonomy-synthesis.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-META-TYPE-FORMALIZATION`](development/meta-type-formalization/) — `candidate` · `artifact` · owner `unscoped`
- [`ART-DSV2-DEFINITIONS`](definitions/) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-METATYPE-DEFINITIONS`](development/meta-type-definitions/) — `candidate` · `artifact` · owner `unscoped`
- [`ART-DSV2-APE`](development/architecture-pattern-enforcement/) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-CODE-TAG-CONFORMANCE`](development/code-tag-conformance/) — `candidate` · `artifact` · owner `unscoped`
- [`ART-DSV2-AGENT-SPEC-CONFORMANCE`](development/agent-spec-conformance/) — `candidate` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR-DECISION`](development/first-production-release/decisions/2026-07-12-product-release-contract.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR-RESEARCH`](development/first-production-release/research/2026-07-12-expanded-capability-frontiers/research.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR-FINDINGS`](development/first-production-release/research/2026-07-12-expanded-capability-frontiers/findings.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR-ROADMAP`](development/first-production-release/ROADMAP.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR-FRONTIER-MANIFEST`](development/first-production-release/craft/expected-node-edge-manifest.yml) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR-FOUNDATION-PLAN`](development/first-production-release/foundation-execution/WORK-PACK.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR-FOUNDATION-ACTIVATION`](development/first-production-release/foundation-execution/work-pack/shared/FOUNDATION-ACTIVATION-DECISION.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR-SGRM007-ACTIVATION`](development/first-production-release/foundation-execution/work-pack/shared/SGRM-007-ACTIVATION-DECISION.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR-SGRM007-REFRESH`](development/first-production-release/foundation-execution/refreshes/2026-07-14-sgrm-007-activation/REFRESH-REPORT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR-W0-PROOF-SYNC-DECISION`](development/first-production-release/foundation-execution/work-pack/shared/W0-PROOF-SYNC-DECISION.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR-W0-PROOF-REFRESH`](development/first-production-release/foundation-execution/refreshes/2026-07-14-w0-proof-sync/REFRESH-REPORT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR01-002-ADOPTION-ACTIVATION`](development/first-production-release/evidence/FPR01-002-ADOPTION-ACTIVATION-DECISION.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR01-002-ACTIVATION-REFRESH`](development/first-production-release/foundation-execution/refreshes/2026-07-16-fpr01-002-adoption-activation/REFRESH-REPORT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR01-002-RECEIPT`](development/first-production-release/foundation-execution/runs/SWU-FPR01-002/TASK-SESSION-RESULT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR01-002-RECEIPT-SYNC`](development/first-production-release/foundation-execution/refreshes/2026-07-16-fpr01-002-receipt-sync/REFRESH-REPORT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR01-003-BASELINE`](development/first-production-release/authority-baseline.yml) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR01-003-VALIDATOR`](development/first-production-release/tools/validate-authority-baseline.cjs) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR01-003-RECEIPT`](development/first-production-release/foundation-execution/runs/SWU-FPR01-003/TASK-SESSION-RESULT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR01-003-BLOCKER-SYNC`](development/first-production-release/foundation-execution/refreshes/2026-07-16-fpr01-003-blocker-sync/REFRESH-REPORT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR-VISIBILITY-PLAN`](development/first-production-release/visibility/WORK-PACK.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR-VISIBILITY-BUILDER`](development/first-production-release/visibility/tools/build-roadmap.py) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR-VISIBILITY-DATA`](development/first-production-release/visibility/roadmap-data.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR-VISIBILITY-HTML`](development/first-production-release/visibility/roadmap.html) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR01003-GUARD-RECEIPT`](development/first-production-release/foundation-execution/runs/SWU-FPR01003-GUARD-001/TASK-SESSION-RESULT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR01003-SAMPLE-RECEIPT`](development/first-production-release/foundation-execution/runs/SWU-FPR01003-SAMPLE-001/TASK-SESSION-RESULT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR01003-REPLAY-RESULT`](development/first-production-release/foundation-execution/runs/SWU-FPR01-003/replay-result.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR01003-PASS-SYNC`](development/first-production-release/foundation-execution/refreshes/2026-07-17-fpr01-003-pass-sync/REFRESH-REPORT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR01-004-RATIFICATION`](development/first-production-release/evidence/authority-baseline-ratification.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR01-004-RECEIPT`](development/first-production-release/foundation-execution/runs/SWU-FPR01-004/TASK-SESSION-RESULT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR01-004-SYNC`](development/first-production-release/foundation-execution/refreshes/2026-07-17-fpr01-004-ratification-sync/REFRESH-REPORT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-LANE-CONTRACT`](development/first-production-release/profile-lanes/fpr02-lanes.yml) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-BACKEND-DECISION`](development/first-production-release/decisions/2026-07-17-fpr02-supported-profile-decision.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-UI-PLAN`](development/ui-profile-implementation/WORK-PACK.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-LANE-REFRESH`](development/first-production-release/foundation-execution/refreshes/2026-07-17-fpr02-lane-separation/REFRESH-REPORT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-BTE-PLAN`](development/first-production-release/backend-type-test-engine-completeness/PLAN.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-IOLM-CONSUMER`](../../cyberAlchemy-v2/development/interactive-ontology-learning-map/SPEC.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-BODY-WAR-CONSUMER`](../../cyberAlchemy-v2/development/domainspec-v2/BODY-WAR-CONSUMER.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-INTEGRATED-MANIFEST`](../../cyberAlchemy-v2/development/domainspec-v2/INTEGRATED-EVIDENCE-MANIFEST.yml) — `candidate` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-INTEGRATED-REFRESH`](../../cyberAlchemy-v2/development/domainspec-v2/refreshes/2026-07-17-fpr02-integrated-consumer-proof/REFRESH-REPORT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-BTE-SWU001-CONTEXT`](development/first-production-release/backend-type-test-engine-completeness/work-pack/session-evidence/SWU-BTE-001/CONTEXT-PACK.md) — `superseded` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-BTE-SWU001-BLOCK-RECEIPT`](development/first-production-release/backend-type-test-engine-completeness/work-pack/session-evidence/SWU-BTE-001/execution-receipt.json) — `superseded` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-BTE-L0A-EXECUTION-RECEIPT`](development/first-production-release/backend-type-test-engine-completeness/work-pack/session-evidence/SWU-BTE-L0A-001/20260723T020759Z-contract-publication/execution-receipt.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-BTE-L0A-CONTINUATION-HANDOFF`](development/first-production-release/backend-type-test-engine-completeness/work-pack/session-evidence/SWU-BTE-L0A-001/20260723T020759Z-contract-publication/continuation-handoff.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-BTE-L0A-PUBLICATION-RECEIPT`](development/first-production-release/backend-type-test-engine-completeness/runs/20260723T020759Z/l0a/contract-publication-receipt.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-BTE-L0A-RECONCILIATION`](development/first-production-release/backend-type-test-engine-completeness/refreshes/2026-07-23-l0a-evidence-reconciliation/REFRESH-REPORT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-BTE-L0A-REPAIR-RECEIPT`](development/first-production-release/backend-type-test-engine-completeness/work-pack/session-evidence/SWU-BTE-L0A-REPAIR-001/20260723T100352Z-exact-byte-repair/execution-receipt.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FPR02-BTE-L0A-REPAIR-SYNC`](development/first-production-release/backend-type-test-engine-completeness/refreshes/2026-07-23-l0a-repair-receipt-sync/REFRESH-REPORT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FIRST-STABLE-FOUNDATION-DECISION`](development/first-production-release/decisions/2026-08-16-first-stable-foundation-candidate.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-STABILITY-REVIEW-CLOSEOUT`](development/reviews/2026-08-14-first-production-stable-implementation/CLOSEOUT-RECEIPT.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-STABILITY-REVIEW-FINDINGS`](development/reviews/2026-08-14-first-production-stable-implementation/findings.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-SFC-AUTHORING-RECEIPT`](development/first-production-release/stable-foundation-cli/AUTHORING-RECEIPT.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-SFC-EXECUTION-ENTRY`](development/first-production-release/stable-foundation-cli/EXECUTION-ENTRY.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-SFC-WORK-PACK`](development/first-production-release/stable-foundation-cli/WORK-PACK.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-SFC-INTEGRATION-VALIDATION`](development/first-production-release/stable-foundation-cli/INTEGRATION-VALIDATION.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-RMT001-TERMINAL`](development/remaining-meta-types/TERMINAL-RECEIPT.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-RMT002-TRANSIENT-PROPOSAL`](development/architecture-pattern-enforcement/refreshes/20260816T160301Z-wp-rmt-002-task-session-transient-output-api-proposal/PROPOSAL-RECEIPT.json) — `superseded` · `artifact` · owner `unscoped`
- [`ART-DSV2-RMT002-TRANSIENT-VALIDATION`](development/architecture-pattern-enforcement/refreshes/20260816T160301Z-wp-rmt-002-task-session-transient-output-api-proposal/VALIDATION-RESULT.json) — `superseded` · `artifact` · owner `unscoped`
- [`ART-DSV2-RMT002-GOVERNANCE-DEFECT`](development/architecture-pattern-enforcement/refreshes/20260816T120821Z-wp-rmt-002-execution-contract-refresh-proposal/governance-defect/GOVERNANCE-DEFECT-RECEIPT.json) — `superseded` · `artifact` · owner `unscoped`
- [`ART-DSV2-FORM-IMPLEMENTATION-QUEUE`](development/ontology-form-decisions/IMPLEMENTATION-QUEUE.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FORM-DECISION-MATRIX`](development/ontology-form-decisions/FORM-DECISION-MATRIX.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-SICL-REPAIR-B-RESULT`](development/system-integration-contract-layer/SIC-FAC-000-REPAIR-B/RESULT.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-SICL-GOVERNANCE-SIDECAR`](development/system-integration-contract-layer/SIC-FAC-000-REPAIR-B-GOVERNANCE-DEFECT/SIDECAR-RECEIPT.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-SMO-REFINE-RESULT`](development/refinement-runs/20260814T103237-0300-shared-meta-obligation-product-readiness/RESULT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-SMO-ONE-SHOT-BLOCK`](development/refinement-runs/20260814T103237-0300-shared-meta-obligation-product-readiness/TASK-SESSION-ONE-SHOT-RESULT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-SMO-G1-REPAIR-RECEIPT`](development/refinement-runs/20260814T103237-0300-shared-meta-obligation-product-readiness/governance-sidecar/g1-material-apply-repair-005/lifecycle/validation/G1-REPAIR-RECEIPT.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FMP-RESULT`](development/refinement-runs/20260816T153610Z-formal-model-proof-provider/RESULT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FMP-WORK-PACK`](development/refinement-runs/20260816T153610Z-formal-model-proof-provider/stages/09-invoke-plan/WORK-PACK.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-IMPL-CONFORMANCE-DEFINE`](development/implementation-conformance/DEFINE-RESULT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-IMPL-CONFORMANCE-ARCH`](development/implementation-conformance/ARCHITECTURE.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-EVF-WORK-PACK`](development/evolvable-validation-framework/WORK-PACK.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-EVF-ONE-SHOT-READINESS`](development/evolvable-validation-framework/development/refinement-runs/20260813T160957-0300-evf-one-shot-readiness/RESULT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-MTF-EXECUTION-STATE`](development/meta-type-realization-factory/EXECUTION-STATE.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-MTF-REPRODUCIBILITY`](development/meta-type-factory-reproducibility/PROTOTYPE-VALIDATION-REPORT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-SFC-OWNER-REVIEW`](.craft/artifacts/2026-08-19-wp-sfc-001-owner-review.md) — `superseded` · `artifact` · owner `unscoped`
- [`ART-DSV2-SFC-CROSS-TASK-GAPS`](development/first-production-release/stable-foundation-cli/work-pack/shared/CROSS-TASK-GAPS.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-SFC-CLOSEOUT-CONTRACT`](development/first-production-release/stable-foundation-cli/work-pack/shared/CLOSEOUT-CONTRACT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-P2-RATIFICATION-PROPOSAL`](.craft/artifacts/2026-08-19-p2-profile-ratification-proposal.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-SMO-PROFILE-CANDIDATE`](development/refinement-runs/20260814T103237-0300-shared-meta-obligation-product-readiness/proposals/formation/supported-profiles.candidate.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-LIVE-PROFILE-REGISTRY`](definitions/minted-project/supported-profiles.yml) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-P2-COUNT-PATCH`](.craft/artifacts/2026-08-19-p2-membership-count-patch-proposal.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FMT-WORK-PACK`](development/format-honesty/WORK-PACK.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FMT-EXECUTION-ENTRY`](development/format-honesty/EXECUTION-ENTRY.json) — `superseded` · `artifact` · owner `unscoped`
- [`ART-DSV2-FMT-SIDECAR`](development/format-honesty/governance-defect/SIDECAR-RECEIPT.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FMT-CHAIN-RECORD`](development/format-honesty/CHAIN-RECORD.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-FMT-REFINE-RESULT`](development/refinement-runs/20260819T000000Z-serialization-format-normalization/RESULT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-RMT002-PROTOTYPE-VALIDATION`](../../.task-session/runs/20260821T092317Z-wp-rmt-002-fast-lane/PROTOTYPE-VALIDATION.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-RMT002R-WORK-PACK`](development/refinement-runs/20260814T193343Z-active-meta-type-implementations/stages/09-invoke-plan/reconciliation/WORK-PACK.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-RMT002R-TERMINAL`](development/remaining-meta-types/reconciliation/wp-rmt-002r/TERMINAL-RECEIPT.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-EVF-L2-PROTOTYPE`](development/evolvable-validation-framework/evidence/SWU-GCP-007-C3/attempt-001/PROTOTYPE-VALIDATION-REPORT.md) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-EVF-L2-CLOSURE`](development/evolvable-validation-framework/development/refinement-runs/20260821T044428Z-evf-l2-one-shot-work-pack/closure-runs/attempt-001/INDEPENDENT-CLOSURE-RECEIPT.json) — `active` · `artifact` · owner `unscoped`
- [`ART-DSV2-CRAFT-REFRESH-20260823`](.craft/ledger.yml) — `active` · `craft-ledger-refresh` · owner `CTX-DSV2-ROOT`
- [`ART-DSV2-APE-WORK-PACK`](development/architecture-pattern-enforcement/WORK-PACK.md) — `active` · `work-pack` · owner `CTX-DSV2-APE`
- [`ART-DSV2-APE-OP-VERIFICATION`](development/architecture-pattern-enforcement/evidence/WP-APE-OP-PROFILE-001/WORK-PACK-VERIFICATION.json) — `pass` · `work-pack-verification` · owner `CTX-DSV2-APE`
- [`ART-DSV2-APE-WF-VERIFICATION`](development/architecture-pattern-enforcement/evidence/WP-APE-WF-PROFILE-001/WORK-PACK-VERIFICATION.json) — `pass` · `work-pack-verification` · owner `CTX-DSV2-APE`
- [`ART-DSV2-BMC-REFINE-RESULT`](development/refinement-runs/20260822T105053Z-backend-meta-type-continuation/RESULT.md) — `pass` · `refine-result` · owner `CTX-DSV2-BMC`
- [`ART-DSV2-BMC-EVD-RECEIPT`](development/backend-meta-type-conformance/evidence/WP-BMC-001/BMC-EVD-001.RECEIPT.json) — `flag` · `evidence-receipt` · owner `CTX-DSV2-BMC`
- [`ART-DSV2-BMC-MATURITY-MATRIX`](development/backend-meta-type-conformance/evidence/WP-BMC-001/BMC-EVD-001.MATURITY-MATRIX.json) — `flag` · `maturity-matrix` · owner `CTX-DSV2-BMC`
- [`ART-DSV2-BMC-REL-PACKET`](development/relationship-constraint-decisions/BMC-REL-001/candidates/BMC-REL-001.RELATIONSHIP-CONSTRAINT-DECISION-PACKET.json) — `block` · `decision-packet` · owner `CTX-DSV2-BMC-REL`
- [`ART-DSV2-BMC-REL-DESIGN-RESULT`](development/relationship-constraint-decisions/BMC-REL-001/sidecars/BMC-REL-CONSTRAINT-COMPLETION/design/DESIGN-RESULT.md) — `superseded` · `design-result` · owner `CTX-DSV2-BMC-REL`
- [`ART-DSV2-BMC-REL-N05-SELECTION`](development/relationship-constraint-decisions/BMC-REL-001/sidecars/BMC-REL-CONSTRAINT-COMPLETION/design/continuations/N05-OWNS-CYCLE-POLICY-GOVERNANCE/decisions/BMC-REL-NONNUMERIC-05-OWNER-SELECTION-RECEIPT.json) — `pass` · `owner-selection-receipt` · owner `CTX-DSV2-BMC-REL`
- [`ART-DSV2-BMC-REL-N45-CLOSEOUT`](development/relationship-constraint-decisions/BMC-REL-001/sidecars/BMC-REL-CONSTRAINT-COMPLETION/design/continuations/N37-EMITS-TARGET-MAX-CLOSURE-PROOF-SHAPE/research/closure-evidence-ownership-r1/define/closure-evidence-contract-r1/design/representation-r1/continuations/N45-EMITS-CLOSURE-EVIDENCE-CHAIN-CONTRACT-ADMISSION/DESIGN-CLOSEOUT-RECEIPT.json) — `pass` · `design-closeout-receipt` · owner `CTX-DSV2-BMC-REL`
- [`ART-DSV2-BMC-REL-EVF-CANDIDATE-STAGING`](development/relationship-constraint-decisions/BMC-REL-001/sidecars/BMC-REL-CONSTRAINT-COMPLETION/design/continuations/N37-EMITS-TARGET-MAX-CLOSURE-PROOF-SHAPE/research/closure-evidence-ownership-r1/define/closure-evidence-contract-r1/plan/closure-evidence-chain-contract-r1/preacceptance/candidate-v1/STAGING-VALIDATION-RECEIPT.json) — `flag` · `staged-candidate-validation-receipt` · owner `CTX-DSV2-BMC-REL`
- [`ART-DSV2-BMC-REL-CANDIDATE-REVIEW`](development/relationship-constraint-decisions/BMC-REL-001/sidecars/BMC-REL-CONSTRAINT-COMPLETION/design/continuations/N37-EMITS-TARGET-MAX-CLOSURE-PROOF-SHAPE/research/closure-evidence-ownership-r1/define/closure-evidence-contract-r1/plan/closure-evidence-chain-contract-r1/preacceptance/reviews/CANDIDATE-V1-PARENT-REVIEW.json) — `pass` · `independent-candidate-review` · owner `CTX-DSV2-BMC-REL`
- [`ART-DSV2-BMC-REL-PREACCEPTANCE-DEFECT`](development/relationship-constraint-decisions/BMC-REL-001/sidecars/BMC-REL-CONSTRAINT-COMPLETION/design/continuations/N37-EMITS-TARGET-MAX-CLOSURE-PROOF-SHAPE/research/closure-evidence-ownership-r1/define/closure-evidence-contract-r1/plan/closure-evidence-chain-contract-r1/governance-defects/preacceptance-non-json-postimage-r1/RECEIPT.json) — `resolved` · `governance-defect-receipt` · owner `CTX-DSV2-BMC-REL`
- [`ART-DSV2-BMC-REL-GOV-REPAIR-SELECTION`](development/relationship-constraint-decisions/BMC-REL-001/sidecars/BMC-REL-CONSTRAINT-COMPLETION/design/continuations/N37-EMITS-TARGET-MAX-CLOSURE-PROOF-SHAPE/research/closure-evidence-ownership-r1/define/closure-evidence-contract-r1/plan/closure-evidence-chain-contract-r1/governance-defects/preacceptance-non-json-postimage-r1/OWNER-SELECTION-RECEIPT.json) — `pass` · `governance-repair-owner-selection` · owner `CTX-DSV2-BMC-REL`
- [`ART-DSV2-BMC-REL-GOV-REPAIR-APPLY`](development/relationship-constraint-decisions/BMC-REL-001/sidecars/BMC-REL-CONSTRAINT-COMPLETION/design/continuations/N37-EMITS-TARGET-MAX-CLOSURE-PROOF-SHAPE/research/closure-evidence-ownership-r1/define/closure-evidence-contract-r1/plan/closure-evidence-chain-contract-r1/governance-defects/preacceptance-non-json-postimage-r1/REPAIR-APPLY-RECEIPT.json) — `pass` · `governance-repair-apply-receipt` · owner `CTX-DSV2-BMC-REL`
- [`ART-DSV2-BMC-REL-CRAFT-FRONTIER-BINDING`](.craft/artifacts/BMC-REL-FRONTIER-BINDING.json) — `active` · `craft-frontier-binding` · owner `CTX-DSV2-BMC-REL`
- [`ART-DSV2-BMC-REL-CRAFT-FRONTIER-VALIDATOR`](.craft/artifacts/validate-bmc-rel-frontier.mjs) — `pass` · `craft-frontier-validator` · owner `CTX-DSV2-BMC-REL`
- [`ART-DSV2-PROOF-SYNTAX-CANDIDATE`](development/proof-obligation-substrate/2026-08-22-top03-shared-syntax-adoption-candidate.md) — `stale` · `adoption-candidate` · owner `CTX-DSV2-PROOF-OBLIGATION-SUBSTRATE`
- [`ART-DSV2-PROOF-SYNTAX-ACCEPTANCE`](authority/decisions/2026-08-22-top03-shared-syntax-adoption-acceptance.md) — `pass` · `owner-acceptance` · owner `CTX-DSV2-PROOF-OBLIGATION-SUBSTRATE`
- [`ART-DSV2-SPEC-ONTOLOGY-DECISION`](development/spec-ontology-branch-decision/decision-gate/DECISION.md) — `pass` · `architecture-decision` · owner `CTX-DSV2-SPEC-ONTOLOGY`
- [`ART-DSV2-SPEC-ONTOLOGY-R4-OWNER-DECISION`](development/spec-ontology-branch-decision/invoke-design/20260823T222046Z-spec-ontology-contract-hardening-r4/owner-admission/RONDELLI-AGGREGATE-DECISION.json) — `flag` · `owner-decision` · owner `CTX-DSV2-SPEC-ONTOLOGY`
- [`ART-DSV2-SPEC-ONTOLOGY-R4-VERIFIER-REQUEST`](development/spec-ontology-branch-decision/invoke-design/20260823T222046Z-spec-ontology-contract-hardening-r4/owner-admission/VICTOR-VERIFIER-REQUEST.json) — `block` · `verifier-request` · owner `CTX-DSV2-SPEC-ONTOLOGY`
- [`ART-DSV2-EVF-RUNTIME-OWNER-ACCEPTANCE`](development/evolvable-validation-framework/dispatch-runs/20260823T140821Z-p0-owner-evidence-review/runtime-repair-candidate/OWNER-ACCEPTANCE-RECEIPT.json) — `pass` · `owner-acceptance` · owner `CTX-DSV2-EVF`
- [`ART-DSV2-EVF-OWNER-PACKET-RECEIPT`](development/evolvable-validation-framework/owner-response-packets/20260823T195640Z-runtime-repair-and-p0/RECEIPT.json) — `flag` · `owner-packet-preparation` · owner `CTX-DSV2-EVF`
- [`ART-DSV2-EVF-PROOF-ENGINE-RECONCILIATION`](development/evolvable-validation-framework/decision-runs/20260823T201735Z-dirty-baselines/PROOF-ENGINE-RECONCILIATION-RECEIPT.json) — `pass` · `reconciliation-receipt` · owner `CTX-DSV2-EVF`
- [`ART-DSV2-EVF-S1-BINDING-REPAIR`](development/evolvable-validation-framework/decision-runs/20260823T201735Z-dirty-baselines/S1-BINDING-REPAIR-RECEIPT.json) — `pass` · `repair-receipt` · owner `CTX-DSV2-EVF`
- [`ART-DSV2-EVF-FORMAT-BASELINE`](development/evolvable-validation-framework/decision-runs/20260823T201735Z-dirty-baselines/FORMAT-HONESTY-BASELINE-RECEIPT.json) — `pass` · `validation-receipt` · owner `CTX-DSV2-EVF`
- [`ART-DSV2-FMT-SWU001-RESULT`](development/format-honesty/runs/SWU-FMT-001/TASK-SESSION-RESULT.json) — `flag` · `task-session-result` · owner `CTX-DSV2-FORMAT-HONESTY`
- [`ART-DSV2-SFC-SOURCE-REFRESH`](development/first-production-release/stable-foundation-cli/refreshes/20260821T210000Z-wp-sfc-001-source-binding-fast-lane/REFRESH-REPORT.json) — `pass` · `refresh-report` · owner `CTX-DSV2-SFC`
- [`ART-DSV2-ORODI-RESEARCH`](development/research/2026-08-24-operational-resilience-observability-deployment-integration/findings.md) — `pass` · `audited-research-finding` · owner `CTX-DSV2-ORODI`
- [`ART-DSV2-ORODI-INVOKE-DEFINE`](development/operational-resilience-observability-deployment-integration/invoke-define/20260824T165443Z-orodi-v1/SPEC.md) — `pass` · `invoke-define-spec` · owner `CTX-DSV2-ORODI`
- [`ART-DSV2-ORODI-INVOKE-DESIGN`](development/operational-resilience-observability-deployment-integration/invoke-design/20260824T165443Z-orodi-v1/ARCHITECTURE.md) — `pass` · `invoke-design-bundle` · owner `CTX-DSV2-ORODI`
- [`ART-DSV2-ORODI-INVOKE-PLAN`](development/operational-resilience-observability-deployment-integration/invoke-plan/20260824T165443Z-orodi-v1/WORK-PACK.md) — `flag` · `invoke-plan-work-pack` · owner `CTX-DSV2-ORODI`
- [`ART-DSV2-ORODI-OWNER-BINDING-DECISION`](development/operational-resilience-observability-deployment-integration/owner-binding-decision/20260824T174431Z-orodi-owner-binding-gate/DECISION-GATE.md) — `pass` · `decision-gate-result` · owner `CTX-DSV2-ORODI`
- [`ART-DSV2-REALIZATION-KERNEL-FAMILIES`](impl/architecture-conformance/) — `canonical` · `implementation-frontier` · owner `CTX-DSV2-REALIZATION-KERNEL`
- [`ART-DSV2-META-TYPE-STATE`](.craft/artifacts/META-TYPE-STATE.json) — `active` · `craft-state-binding` · owner `CTX-DSV2-ROOT`
- [`ART-DSV2-META-TYPE-STATE-VALIDATOR`](.craft/artifacts/validate-meta-type-state.mjs) — `pass` · `craft-state-validator` · owner `CTX-DSV2-ROOT`
- [`ART-DSV2-META-TYPE-BASELINE-DECISION`](development/meta-type-instantiation-cli/OWNER-CANONICAL-DOCS-AND-BASELINE-V2-DECISION.json) — `pass` · `owner-baseline-decision` · owner `CTX-DSV2-REALIZATION-KERNEL`
- [`ART-DSV2-META-TYPE-BASELINE`](development/meta-type-instantiation-cli/CANONICAL-IMPLEMENTED-BASELINE.v2.json) — `pass` · `canonical-implemented-baseline` · owner `CTX-DSV2-REALIZATION-KERNEL`
- [`ART-DSV2-META-TYPE-BASELINE-VALIDATOR`](development/meta-type-instantiation-cli/validate-baseline.mjs) — `pass` · `exact-baseline-validator` · owner `CTX-DSV2-REALIZATION-KERNEL`
- [`ART-DSV2-META-TYPE-CLI-PLAN`](development/meta-type-instantiation-cli/IMPLEMENTATION-PLAN.md) — `flag` · `implementation-plan` · owner `CTX-DSV2-IMPL-CONFORMANCE`
- [`ART-DSV2-META-TYPE-CURRENT-IMPLEMENTATION`](definitions/meta-types/current-implementation.json) — `pass` · `canonical-current-implementation-state` · owner `CTX-DSV2-REALIZATION-KERNEL`
- [`ART-DSV2-META-TYPE-ONTOLOGY-STATE`](development/implementation-conformance/ontology-experiment/ontology.json) — `pass` · `architecture-property-ontology` · owner `CTX-DSV2-IMPL-CONFORMANCE`
- [`ART-DSV2-META-TYPE-ONTOLOGY-PROJECTION`](development/implementation-conformance/ontology-experiment/domain-meta-types.projection.json) — `pass` · `canonical-meta-type-projection` · owner `CTX-DSV2-IMPL-CONFORMANCE`
- [`ART-DSV2-META-TYPE-ONTOLOGY-MATERIALIZER`](development/implementation-conformance/ontology-experiment/materialize-current-meta-type-state.mjs) — `pass` · `deterministic-ontology-materializer` · owner `CTX-DSV2-IMPL-CONFORMANCE`
- [`ART-DSV2-META-TYPE-ENFORCEMENT-ASSETS`](.craft/artifacts/META-TYPE-ENFORCEMENT-ASSETS.json) — `active` · `meta-type-enforcement-asset-registry` · owner `CTX-DSV2-ROOT`
- [`ART-DSV2-META-TYPE-ENFORCEMENT-ASSETS-SCHEMA`](.craft/artifacts/meta-type-enforcement-assets.schema.json) — `active` · `meta-type-enforcement-asset-schema` · owner `CTX-DSV2-ROOT`
- [`ART-DSV2-META-TYPE-ENFORCEMENT-ASSETS-VALIDATOR`](.craft/artifacts/validate-meta-type-enforcement-assets.mjs) — `pass` · `meta-type-enforcement-asset-validator` · owner `CTX-DSV2-ROOT`

## Definition index

- `DEF-DSV2-TWO-PLANE` — **two-plane boundary** (`candidate`): Ontology framing wins on the spec-AUTHORING plane; derivation stays primary on the engine-facing CONTRACT plane; authority flows contract -> authoring, never reverse.
- `DEF-DSV2-EXEC-GRAPH` — **executable typed graph** (`candidate`): The v2 spec as taxonomy (nodes) + edges (edge-law) + composability (how node-patterns compose in code), governed by layering / validation / drift with two enforcement arms (engine derivation + code-tag).
- `DEF-DSV2-EDGE-ADMISSIBILITY` — **edge-law admissibility** (`candidate`): An edge type is admissible only if it composes into different code (adds a non-redundant distinction); otherwise the distinction folds into the node type or an explicit typed coupling flag. A domain specialization of CAV2-D22 / D29 / D16 (governance orthogonality, not Lean/Hilbert).
- `FPR-D01` — **BO** (`candidate`): Finite governed business concept, relation, rule, and constraint schema with stable IDs, provenance, and contradiction policy.
- `FPR-D02` — **BK** (`candidate`): Profile-scoped asserted business nodes, edges, rules, and constraints instantiating BO; not a synonym for ontology.
- `FPR-D03` — **B** (`candidate`): Contract business plane composed of BO, BK, provenance, and an authority receipt.
- `FPR-D04` — **Spec** (`candidate`): Owner-promoted authoritative DomainSpec definitions, registries, and selected feature-pack sources.
- `FPR-D05` — **Sg** (`candidate`): Deterministic total typed projection normalize(Spec,P) with source anchors; never parallel semantic authority.
- `FPR-D06` — **G** (`candidate`): Internal compiler IR produced by encoding Sg; not a contract semantic plane.
- `FPR-D07` — **A_req** (`candidate`): Normative architecture requirements graph with finite layers, admissibility, forbidden dependencies, patterns, and path obligations; no observed imports or calls.
- `FPR-D08` — **F_struct** (`candidate`): Bounded relational structural projection with source map, abstraction, solver, bounds, timeout, and result taxonomy.
- `FPR-D09` — **F_state** (`candidate`): Bounded state/transition projection for reachability, invariants, deadlock, and declared liveness or fairness.
- `FPR-D10` — **O_spec(P)** (`candidate`): Independent authority-owned expected obligation set for the exact supported profile P.
- `FPR-D11` — **Expected(o)** (`candidate`): Expected predicate or value rooted in promoted Spec, possibly referencing accepted B; never inferred from tests or implementation output.
- `FPR-D12` — **Req_spec(o)** (`candidate`): Closed set of required evidence classes and expected outcomes for obligation o.
- `FPR-D13` — **T_gen** (`candidate`): Generated executable verification program or artifact; neither execution evidence nor its own oracle.
- `FPR-D14` — **E_run** (`candidate`): Candidate, profile, and tool-bound static, formal, execution, and mutation receipts; evidence rather than authority.
- `FPR-D15` — **I_struct** (`candidate`): Observation graph over frozen code roots under pinned parser/tool semantics; tags are correspondence claims.
- `FPR-D16` — **cross_graph_conformance_vector** (`candidate`): Machine vector of named directional predicates; contract and internal-assurance predicates remain segregated and owner judgment cannot set a pass bit.
- `FPR-D17` — **profile/structural conformance verdict** (`candidate`): Machine result that required sources satisfy the frozen profile and structural rules; it does not accept implementation or authorize release.
- `FPR-D18` — **mapping-predicate verdict** (`candidate`): Machine result for one named directional predicate under explicit bounds, algorithm version, and result taxonomy.
- `FPR-D19` — **implementation-conformance acceptance** (`candidate`): Implementation/platform-owner decision made only after all applicable technical predicates and evidence pass.
- `FPR-D20` — **release authorization** (`candidate`): External-owner authorization of exact bits, claims, actors, channel, compatibility, support, and withdrawal after independent verification.
- `FPR-D21` — **node-ready** (`candidate`): One named roadmap node has closed dependencies, present inputs, assigned execution owner, and no inbound block.
- `FPR-D22` — **roadmap-ready-for-execution** (`candidate`): Every first executable node is node-ready, candidate definitions are tracked, and the Craft expected-state manifest is instantiated and validated.
- `FPR-D23` — **release-ready** (`candidate`): Every contract-required pre-release node and gate has passed for one exact candidate.
- `FPR-D24` — **production-authorized** (`candidate`): Release authorization exists for one exact artifact and configuration under named actors, environment, compatibility, support, and withdrawal boundaries.

## Export receipt

- Source ledger: [`.craft/ledger.yml`](.craft/ledger.yml)
- Refresh date: `2026-08-24`
- Helper audit: joined; no helper writes
- Mutation scope: the ORODI Decision Gate, this Craft ledger and human view, plus non-authoritative observability telemetry only
- Authority effect: limited Wave-0 packet coordination only; no field-level, execution, infrastructure, deployment, promotion or release authority
- Latest update: live ORODI subject/environment binding is explicitly deferred. The context remains `plan` / `block`; the current Work Pack has zero executable units, and no product, Task Session, infrastructure, deployment, promotion or release route was opened.
