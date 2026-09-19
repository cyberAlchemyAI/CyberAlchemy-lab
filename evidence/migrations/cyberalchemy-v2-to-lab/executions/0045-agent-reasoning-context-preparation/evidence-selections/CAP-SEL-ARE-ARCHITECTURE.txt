---
title: Agent Reasoning Engine Candidate Architecture
status: candidate-design-with-promoted-bounded-l0-witness
invoke_mode: design
scope: private-cav2-development
authority_effect: none
---

# Agent Reasoning Engine candidate architecture

This design turns the approved definition into a six-view architecture. It is a
plan-ready whole-engine candidate, not evidence that this checkout is a promoted
reasoning engine. Its first executable slice, `semantic-judgment evaluator@1`,
is promoted as the bounded local L0 witness; every higher runtime and
integration layer remains candidate.

## Source contracts

- [`../spec/SPEC.md`](../spec/SPEC.md)
- [`../spec/GLOSSARY.md`](../spec/GLOSSARY.md)
- [`../spec/INTENT-RECORD.md`](../spec/INTENT-RECORD.md)
- [`../spec/INTENT-SCHEMA-DECISION.md`](../spec/INTENT-SCHEMA-DECISION.md)
- [`../receipts/engine-define-reconciled.json`](../receipts/engine-define-reconciled.json)
- [`../../../implementation/agent-reasoning-engine/generated/runs/evaluator-v1-20260723T-session-001/TERMINAL-RECEIPT.json`](../../../implementation/agent-reasoning-engine/generated/runs/evaluator-v1-20260723T-session-001/TERMINAL-RECEIPT.json)
- [`../decisions/g-are-l0-promotion/PROMOTION-RECEIPT.json`](../decisions/g-are-l0-promotion/PROMOTION-RECEIPT.json)
- [`../../../authority/definitions/DEFINITIONS.md`](../../../authority/definitions/DEFINITIONS.md), especially CAV2-D34 through D41 and D56
- [`../../../../projects/cyberalchemy-orchestrator/docs/research/2026-07-22-agent-reasoning-engine-contract/findings.md`](../../../../projects/cyberalchemy-orchestrator/docs/research/2026-07-22-agent-reasoning-engine-contract/findings.md)

### External candidate alignment sources

- [ACI ADR-001](../../../../projects/cyberalchemy-orchestrator/docs/features/agents-communication-infra/adrs/ADR-001-persistence-replay-and-canonical-contracts.md)
  is accepted for its W0 decision scope; the ACI runtime gate remains blocked.
- The [ACI Work Pack](../../../../projects/cyberalchemy-orchestrator/docs/features/agents-communication-infra/WORK-PACK.md)
  is the current runtime-maturity boundary.
- [Bus Contracts](../../../../projects/cyberalchemy-orchestrator/docs/features/agents-communication-infra/discovery/bus-contracts/README.md)
  remains draft, and its latest
  [integration assessment](../../../../projects/cyberalchemy-orchestrator/docs/features/agents-communication-infra/discovery/spec-integration-assessment/avaliacao-independente-publication-bridge.md)
  has no post-remediation `PASS`.
- The [agent communication protocols](../../../../projects/cyberalchemy-orchestrator/docs/features/agents-communication-infra/discovery/agents-communication-protocols/README.md)
  surface is discovery only.
- The [APT Work Pack](../../../../projects/cyberalchemy-orchestrator/docs/features/agent-provenance-telemetry/WORK-PACK.md)
  is observational and mutation-blocked.

These are comparison evidence, not imported authority or compatibility proof.

## View 1 — context

The candidate sits between governed intent/authority sources and a future exact
effect adapter. It owns a bounded semantic reduction under frozen inputs; it
does not own source authority, real-world truth, canonical promotion, or effect
permission.

```text
operator / intent owner ---- IntentRecord --------+
authority owners ----------- governed sources ----+--> candidate engine
catalog owners ------------- finite manifest -----+          |
subagents / tools ----------- proposed observations           v
                                                    ReasoningReceipt
                                                            |
effect owner --------------- exact-effect Gate <-----------+
                                                            |
future effect adapter <------ only exact pass ---------------+
```

External actors and responsibilities:

| Actor | Supplies | Cannot supply by participation alone |
|---|---|---|
| operator / intent owner | source intent and explicit revision authority | semantic truth or canonical promotion |
| authority-model owner | applicable owner, scope, precedence, expiry, and revocation policy | facts merely by naming them |
| catalog owner | finite rules, evaluator version, challenge and temporal policy | self-authorization |
| subagent or tool | provenance-bearing observations and challenges | authority, confidence, or final judgment |
| entry-gate owner | permission to start one bounded run | effect permission |
| effect-gate owner | permission for one exact effect envelope | a general action capability |
| artifact-admission owner | future durability/admission decisions | retrospective truth or authority |

## View 2 — high-level structure

```text
Intent Projector + Authority Resolver + Catalog Loader
                         |
                         v
                 Entry Gate Adapter
             block/defer | pass
                 zero calls|
                         v
        Effort Controller + Technique Selector
                         |
                         v
            Actor Protocol / Runtime Journal
                         |
                         v
        semantic-judgment evaluator@1 boundary
          [Observation Admitter -> Reducer ->
           ApplicabilityDecision + typed outcome ->
           Receipt Assembler]
                         |
                         v
              Exact-Effect Gate Adapter
              non-positive|positive + pass
               zero calls|one idempotent attempt (future)
```

The architecture has three non-substitutable layers:

1. gates decide controlled transitions;
2. the actor protocol records attempts, events, joins, and replay;
3. the evaluator owns finite catalog applicability and semantic reduction.

A stage cannot borrow the authority or claim of another stage. In particular,
an orchestration success cannot stand in for a semantic outcome, and a positive
semantic outcome cannot stand in for an effect gate.

Evaluator semantics remain reasoning-engine-owned. The accepted
[`ACI-REASONING-BINDING`](aci-reasoning-binding/ARCHITECTURE.md) selects an
ACI-subordinate target: integrated actor-journal facts, canonical acceptance
identity, replay cursor, and effect intents are ACI-owned; semantic derivation
and reasoning-receipt content remain evaluator-owned behind the artifact
boundary. External source maturity and executable conformance still must pass
before compatibility or runtime claims.

## View 3 — low-level components

| Component | Input | Output | Fail-closed responsibility |
|---|---|---|---|
| Intent Projector | raw expression plus selected-local IntentRecord | `ProblemFrame` plus projection digest | unresolved semantic source/revision ownership remains visible |
| Authority Resolver | governed selectors and current owner/status/time state | `AuthoritySnapshot` | model/search output never creates authority |
| Catalog Loader | owner-authorized catalog handle | `RuleCatalogManifest` | reject mutation, expiry, revocation, cycles, and missing ownership |
| Entry Gate Adapter | frame, snapshot, manifest, proposed run envelope | complete entry `GateDecision` | `block/defer` returns before any actor/evaluator call |
| Effort Controller | risk/effect/uncertainty policy inputs | `EffortProfile` | unknown never lowers effort; effort is not evidence |
| Technique Selector | manifest-required candidate obligations plus effort profile | `TechniquePlan` | selection anticipates required checks but never decides final applicability |
| Actor Protocol | plan, budgets, roles, immutable commands | `RuntimeJournal` plus proposed observations/challenges | partial failures and timeouts remain events, not silent defaults |
| Evaluator-owned Observation Admitter | proposed observations plus manifest/snapshot | `ObservationSet` with admitted/rejected posture | deterministic subcomponent; cannot independently alter applicability or outcome |
| Semantic Evaluator | frozen digests, applicable rules, observations, challenge state | one terminal outcome plus `ApplicabilityDecision` | finite deterministic reduction; abstain/escalate on insufficiency |
| Evaluator-owned Receipt Assembler | journal, decision, derivation, outcome, residue | immutable `ReasoningReceipt` | deterministic serializer; cannot independently change derivation, outcome, or residue |
| Effect Gate Adapter | exact effect envelope plus receipt and current authority state | complete effect `GateDecision` | revalidates exact target/scope/action; cannot reuse entry pass |
| Effect Dispatcher | positive outcome plus exact gate pass | idempotent attempt receipt | future boundary only; zero calls otherwise |
| Replay/Revalidation Service | retained run or current source handles | historical replay or fresh result | historical replay performs no model/tool/effect calls |

Detailed contracts are in
[`COMPONENT-CONTRACTS.md`](COMPONENT-CONTRACTS.md).

## View 4 — workflow process

1. Record raw intent and project all seven D39 questions with whole-field
   posture. Unsupported semantic source or revision authority stays unresolved.
2. Construct a bounded `ProblemFrame`; it is not an accepted premise set.
3. Freeze authority and catalog snapshots with digests and temporal state.
4. Evaluate the entry gate and persist the full decision before any actor or
   evaluator event.
5. On entry `block` or `defer`, close with zero actor/evaluator/effect calls. On
   `flag`, route to owner review with zero calls; only a newly recorded `pass`
   may continue.
6. On entry `pass`, derive the minimum policy-required effort and technique plan.
7. Run bounded actors/tools; journal commands, attempts, joins, failures,
   challenges, and stopping conditions.
8. Admit or reject proposed observations under the frozen manifest.
9. Reproduce applicability and reduce the finite rule set to one typed outcome.
10. Persist the `ReasoningReceipt` and unresolved residue.
11. Only for `RecommendedUnderSnapshot`, evaluate a fresh exact-effect gate for
    the identical fixed action envelope.
12. A future dispatcher makes one idempotent attempt only after exact gate
    `pass`; all other paths make zero attempts.

The state and ordering details are in
[`DECISION-AND-EFFECT-FLOW.md`](DECISION-AND-EFFECT-FLOW.md).

## View 5 — decision flow

The semantic outcome algebra is disjoint from D37 gate verdicts:

```text
semantic outcomes:
  InvalidInput | UnauthorizedCatalog | OutOfDomain |
  Ineligible.Defeated | Deferred.Insufficient | EscalateOwner |
  RecommendedUnderSnapshot | Invalidated

gate verdicts:
  pass | flag | block | defer
```

Only `RecommendedUnderSnapshot` is eligible to reach the effect gate. It is
still non-authorizing. Unknown facts, unresolved required ownership, mandatory
challenge timeout, invalid catalog state, temporal drift, or material conflict
cannot default to recommendation.

Effort routing is also separate:

| Tier | Required method shape | Ceiling before another gate |
|---|---|---|
| T0 | frame, concrete sources, owner boundary, residue | read-only preflight or draft |
| T1 | one bounded route with stop/recomposition | narrow recommendation or draft |
| T2 | sequential explorer/auditor plus executable fixtures | eligibility if evidence lanes pass |
| T3 | tensioned explorer/skeptic roles with declared join/cap | challenged recommendation plus residue |
| T4 | protected-action map, exact scopes, validation | exact effect only after effect-gate pass |

Removing evidence, challenge lanes, or owner certainty must never lower the tier
or improve the outcome.

## View 6 — dependency and interface boundaries

| Dependency | Contract consumed | Boundary |
|---|---|---|
| CAV2 definitions | D34–D41, D56 selectors and meanings | referenced, never redefined |
| constitutions | owner-authorized obligations in the frozen snapshot | quotation alone does not establish applicability |
| Dispatch Technique Catalog | concrete method identifiers and checks | technique choice does not decide semantic truth |
| subagent runtime | bounded roles, messages, joins, timeouts | runtime coordination does not own inference |
| model/tool providers | proposed observations with provenance | mutable/non-deterministic calls are never historical replay |
| artifact store | immutable content-addressed records and journals | durability does not imply canonical admission |
| gate implementation | full D37 decision record | two separate instances; entry never aliases effect |
| future effect adapter | exact fixed envelope and idempotency key | outside the first implementation witness |

All inter-component records are versioned and digest-bound. A downstream
consumer rejects unknown versions, missing required digests, stale temporal
state, and cross-run handle substitution.

The interfaces in this view are logical boundaries.
`G-ARE-ACI-BINDING` selected the ACI-subordinate target through
[`BINDING-RECEIPT.json`](../decisions/aci-reasoning-binding/BINDING-RECEIPT.json).
SWU-ARE-002, SWU-ARE-003, and SWU-ARE-006 still may not implement an integrated
writer or claim compatibility until the plan binds them to current ACI
conformance evidence. Local-only witnesses must remain explicitly
non-integrated.

## Failure and degraded behavior

| Condition | Required behavior |
|---|---|
| unresolved semantic source | preserve unresolved; gate/owner policy decides whether run may continue |
| unresolved revision authority | do not invent owner; return owner residue or escalation |
| authority/catalog missing or cyclic | `UnauthorizedCatalog` or `EscalateOwner`; zero effect |
| entry gate block/defer | no actor, evaluator, or effect calls |
| entry gate flag | owner review with zero calls until a new explicit pass |
| subagent/tool partial failure | journal failure; apply explicit quorum/required-lane rule or defer |
| mandatory challenge timeout | `Deferred.Insufficient` |
| unsupported conclusion | `OutOfDomain` |
| grounded defeater | `Ineligible.Defeated` |
| receipt persistence failure | do not call effect gate; close invalid/incomplete |
| effect gate non-pass | zero effect attempts |
| repeated positive delivery | same idempotency key; one logical attempt |
| post-result drift | historical result remains historical; fresh revalidation may return `Invalidated` |
| post-effect late defeat | open incident/compensation route; never claim retroactive authorization |

## Design decisions and risks

| ID | Decision | Reason | Residue/risk |
|---|---|---|---|
| ARE-DES-001 | Keep entry gate, evaluator, and effect gate separate. | Each answers a different authority/semantic question. | Integration could accidentally collapse verdicts; persisted-order tests required. |
| ARE-DES-002 | Keep actor protocol outside the evaluator. | Coordination and inference are not substitutable. | Observation admission boundary must be explicit. |
| ARE-DES-003 | Use finite versioned catalogs for witness 1. | Makes deterministic replay and counterfactual testing possible. | Applicability/precedence owner still unresolved. |
| ARE-DES-004 | Derive effort from owned policy, not model confidence. | More tokens/agents cannot become evidence. | Exact T0–T4 policy values remain planning inputs. |
| ARE-DES-005 | Exclude `AntiBiasVector` from witness 1. | Dimensions/interventions/efficacy are not governed or evidenced. | Blocks anti-bias claims, not generic evaluator planning. |
| ARE-DES-006 | Keep revision-history mechanics outside selected-local intent v1. | No revision-bearing evidence exists. | Future migrations need a separate owner decision. |
| ARE-DES-007 | Separate historical replay from current revalidation. | Mutable source state cannot be smuggled into replay. | Retention and admission posture remains local. |
| ARE-DES-008 | Use the selected ACI-subordinate binding for every future integrated journal, receipt, replay, publication, provenance, and effect-intent mapping. | Prevent a second integrated journal or lifecycle authority from being created by local similarity. | External maturity and conformance receipts remain mandatory; local-only evidence cannot satisfy compatibility. |

## Design validation and handoff

- Six views: complete.
- Glossary consistency: see
  [`GLOSSARY-CONSISTENCY.md`](GLOSSARY-CONSISTENCY.md); no canonical changes.
- Technique trace: `sequence` fixes stage ordering; `x_ray` exposes
  non-substitutable boundaries; `artifact_contract_bridge` binds define outputs;
  `authority_split_gate` separates owner/applicability/effect authority;
  `state_namespace_boundary` separates intent, protocol, semantic, and gate
  state; `scu_swu_reduction` keeps evaluator@1 first; `recomposition_proof`
  reconnects it to the whole boundary; `residue_ledger` preserves open owners.
- Distill design-unit verdict: **pass with residue**. The coherent design unit is
  the end-to-end pre-action boundary because its meaning is the separation among
  gates, protocol, evaluator, and effect. The executable first unit is smaller:
  evaluator@1 plus test doubles and immutable fixtures. Applicability and
  challenge-closure policy block implementation, not plan authoring.
- Layering: plan must produce the required global L0–L3 artifact.
- Binding decision:
  [`G-ARE-ACI-BINDING` option A](../decisions/aci-reasoning-binding/BINDING-RECEIPT.json)
  passes for architecture selection only.
- Next route: Invoke plan for an ACI-subordinate conformance revision; stop
  before Task Session, SWU selection, or implementation.
