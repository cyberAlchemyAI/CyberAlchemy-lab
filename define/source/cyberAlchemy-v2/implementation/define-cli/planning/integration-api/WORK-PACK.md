---
module: define-integration-api
version: candidate-v1
status: l4-testable-candidate
updatedAt: 2026-09-08
docType: work-pack
authority_effect: none
---

# WORK-PACK: Define Integration API

## Control Fields

| Field | Value | Notes |
| --- | --- | --- |
| workPackGateStatus | block | Planning candidate; implementation not authorized and L0 shapes need owner review. |
| complexity | medium | Crosses Define API, compiled Alch, Module Port, ontology adapters, and a Plan consumer. |
| outputMode | split | Tasks and waves are separated below. |
| executionPackRef | [EXECUTION-PACK.md](EXECUTION-PACK.md) | Candidate wave sequence. |
| layeringArtifactRef | [IMPLEMENTATION-LAYERING.md](IMPLEMENTATION-LAYERING.md) | L0–L4 evidence gates. |
| activeLayerWindow | complete-candidate | L0–L4 passed locally; owner review is next, not automatic admission. |
| lastUpdatedAt | 2026-09-08 | Candidate authored date. |
| readinessProfile | pilot | Local deterministic proof, not release readiness. |

## Objective Summary

- Objective: prove a stable Define Client API and extensible ontology-authoring
  adapter boundary without hard-coding future ontologies into Define core.
- Primary inputs: [DESIGN.md](DESIGN.md),
  [IMPLEMENTATION-PLAN.md](IMPLEMENTATION-PLAN.md), and current Define/Module Port code.
- Success: L0–L4 prove the protocol, stable Client API, Product and Business
  dependency chain, configuration-only System extension, and no-effect Plan
  consumption while the zero-adapter Definition Pack path remains unchanged.

## Delivery Slices

| Slice | Outcome | Layer | Wave | Dependencies | Validation |
| --- | --- | --- | --- | --- | --- |
| S0 | Protocol and synthetic stage proof | L0 | W0 | none | compiled-byte, hostile, semantic, and regression tests |
| S1 | Stable consumer facade | L1 | W1 | S0 | CLI/chat/durable parity |
| S2 | Product Ontology vertical | L2 | W2 | S1 | realistic candidate and replay |
| S3 | Business dependency graph | L3 | W3 | S2 | stale/substituted prerequisite rejection |
| S4 | Third adapter and Plan handoff | L4 | W4 | S3 | no-core-edit and consumer-contract proof |

## Task Status Board

| Task | Goal | Layer | Waves | Gate | Status |
| --- | --- | --- | --- | --- | --- |
| [T0](tasks/TASK-T0-PROTOCOL.md) | Contract, Alch, registry, facade, synthetic adapter | L0 | W0 | local-exit-evidence-pass | completed-candidate |
| [T1](tasks/TASK-T1-CLIENT-API.md) | Define Client API and interface migration | L1 | W1 | local-exit-evidence-pass | completed-candidate |
| [T2](tasks/TASK-T2-PRODUCT-ADAPTER.md) | Product Ontology adapter | L2 | W2 | local-exit-evidence-pass | completed-candidate |
| [T3](tasks/TASK-T3-BUSINESS-DEPENDENCY.md) | Business Ontology dependency | L3 | W3 | local-exit-evidence-pass | completed-candidate |
| [T4](tasks/TASK-T4-EXTENSION-HANDOFF.md) | Extension and Plan-consumer proof | L4 | W4 | local-exit-evidence-pass | completed-candidate |
| TV | Full completion verification | L4 | W4 | complete-Define-suite-pass | completed-candidate |

## Smallest Working Units

| SWU | Parent | Dependencies | Write scope | Done criteria | Acceptance evidence | Validation | Owner recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SWU-T0-01 | T0 | none | integration schemas and tests | closed descriptor/result schemas reject hostile shapes | schema fixture results | focused Node tests | Define runtime implementer |
| SWU-T0-02 | T0 | SWU-T0-01 | new integration `.alch` sources and separate generated root | four generic entries compile byte-identically | compiler manifests and second-build comparison | Alch verifier | Alch/DomainSpec implementer |
| SWU-T0-03 | T0 | SWU-T0-01 | ontology-stage-port package and focused tests | zero/synthetic adapter graph and receipts work | positive and hostile receipts | focused Node tests twice | Define runtime implementer |
| SWU-T0-04 | T0 | SWU-T0-02, SWU-T0-03 | integration composition fixture only | one synthetic stage completes end to end | artifact plus handoff receipt | focused tests plus full Define suite | Define runtime implementer |
| SWU-T1-01 | T1 | T0 | client-api package, narrow exports, interface adapters/tests | all eight client operations have closed results | parity matrix | existing and new tests | Define runtime implementer |
| SWU-T2-01 | T2 | T1, product selection | product adapter, its Alch/generated/test roots | real Product candidate exports deterministically | candidate and receipt | adapter plus full suite | Product ontology owner + implementer |
| SWU-T3-01 | T3 | T2 | business adapter and dependency tests | exact Product receipt gates Business only | substitution matrix | dependency tests | Business ontology owner + implementer |
| SWU-T4-01 | T4 | T3 | third adapter fixture/config/tests | ontology added without core source edit | diff allowlist and passing proof | extension test | Define runtime implementer |
| SWU-T4-02 | T4 | SWU-T4-01, Plan schema selection | Plan consumer adapter/contract tests | Plan reads receipt without promotion | consumer acceptance fixture | contract test | Plan owner + Define owner |

Task-local inputs, outputs, ordered rules, edge cases, failure modes, and
verification are specified in the linked task contracts. Only one SWU may be
selected for mutation at a time unless an explicit merge
plan proves disjoint write scopes. Each implementation turn must replace the
candidate path class above with an exact allowlist.

## Blockers

| ID | Scope | Description | Owner | Next action |
| --- | --- | --- | --- | --- |
| B0 | work pack | No implementation authorization in this Plan route. | user / route owner | select a bounded IMPLEMENT objective for one SWU |
| B1 | L0 promotion | Descriptor and receipt shapes passed local candidate tests but are not admitted. | Define runtime owner | review L0 evidence before any promotion claim |
| B2 | plan admission | Goals validation is blocked. | Goals owner | repair independently; do not relabel this plan admitted |
| B3 | T2 | Resolved for this candidate by the selected Alch Product Ontology source. | Product ontology owner | review only; no admission inferred |
| B4 | T4 | Resolved for this candidate by `cav2.plan-ontology-handoff-input/v1`. | Plan owner | review only; canonical registration is separate |

## Gate Checks

1. The work-pack remains blocked until one exact SWU is routed and authorized.
2. L1 cannot begin before L0 exit evidence.
3. Every Alch change must compile through ontology, Craft/DomainSpec, and
   executable projection with byte-identical regeneration.
4. Every stage must preserve grounding, non-collapse, orthogonality, explicit
   confirmation, deterministic receipts, and authority effect none.
5. No task may introduce discovery, fallback, route ownership, admission, or activation.
6. Completion evidence cannot self-promote the plan or produced ontology.

## Recommended Execution Entry

The L0–L4 construction candidate is complete. The next action is owner review of
the exact candidate and evidence. Admission, activation, canonical Plan-schema
registration, isolation, publication, release, or deployment each requires a
separately routed and authorized objective. Do not use task-session.

## Open Questions

Open product and protocol questions are owned by [DESIGN.md](DESIGN.md#open-questions).
