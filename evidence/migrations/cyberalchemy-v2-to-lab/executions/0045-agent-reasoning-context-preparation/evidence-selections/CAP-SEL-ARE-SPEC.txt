---
title: Agent Reasoning Engine Specification
status: candidate-with-promoted-bounded-l0-witness
scope: private-cav2-development
invoke_mode: define
discovery_source: projects/cyberalchemy-orchestrator/docs/research/2026-07-22-agent-reasoning-engine-contract/findings.md
template_family: arcanum/spells/invoke/templates/domainspec-spec/
template_posture: local-adaptation
authority_effect: none
intent_record_selection: selected-local-from-admitted-run-02
---

# Agent Reasoning Engine

## Definition posture

This document defines a candidate whole-engine boundary. One finite local
evaluator slice is implemented and witnessed, but the checkout is not promoted
as a reasoning engine and a semantic outcome cannot authorize an effect.

| Claim | Posture at this stage |
|---|---|
| The repository already has a pre-action reasoning engine | rejected by accepted research |
| The architecture below is a candidate whole-engine boundary | local candidate |
| `semantic-judgment evaluator@1` is the finite first build/test slice | **PROMOTED BOUNDED L0 WITNESS; whole-engine promotion absent** |
| The local IntentRecord treatment was selected from the admitted 12+3 run | selected-local candidate; bounded evidence only |
| The engine reduces bias | not admissible; `AntiBiasVector` is excluded |
| A receipt or multi-agent consensus proves a conclusion | prohibited |

The specification is informed by active CAV2 definitions but creates no CAV2
definition, constitution, authority kind, or public Arcanum contract.

## Template selection and mapping

Invoke Inventory selected the implemented DomainSpec spec baseline at
`arcanum/spells/invoke/templates/domainspec-spec/`. It is eligible because this
stage defines a capability-owned system boundary, a module map, candidate domain
concepts, and downstream consumers. The selection is a local adaptation only:
it neither promotes the template nor publishes this private candidate as
DomainSpec or Arcanum authority.

The dispatch limits this stage to `SPEC.md`, `GLOSSARY.md`, and
`INTENT-RECORD.md`, so unused aspect files from the template family are omitted
instead of fabricated. Template concerns map as follows:

| DomainSpec baseline concern | Local section or companion |
|---|---|
| What the module owns | [Desired capability](#desired-capability) and [Non-goals](#non-goals) |
| Module map | [Candidate system boundary](#candidate-system-boundary) |
| Capabilities | [Functional requirements](#functional-requirements) |
| Domain concepts / registry | [Local candidate records](#local-candidate-records) and [Glossary](GLOSSARY.md) |
| Source intent | [Candidate intent record](INTENT-RECORD.md) |
| Dependencies / consumers | [Governed source contracts](#governed-source-contracts) and [Next route](#next-route) |

## Intent

Give agents a governed, traceable way to preserve source intent, select
risk-sensitive reasoning methods, derive typed semantic judgments, abstain when
support is insufficient, and withhold every effect until a separate exact-action
gate passes.

The engine must address four pressures:

1. Source intent can be silently replaced by inferred scope, a convenient
   artifact, a preferred solution, or an implementation shortcut.
2. Constitutions and methods can be cited without proving that they apply to the
   current problem.
3. More effort, agents, tokens, agreement, or receipts can be mistaken for more
   truth or authority.
4. A valid semantic recommendation can be mistaken for permission to act.

The source intent is represented by the selected-local candidate in
[`INTENT-RECORD.md`](INTENT-RECORD.md). The admitted run-02 population evidence
and explicit g6 owner decision selected its local treatment; neither the run nor
the decision promotes a CAV2 definition, proves semantic truth, or makes the
record universally fit.

## Desired capability

For one bounded problem and one frozen authority/catalog state, the candidate
engine should be able to:

- preserve an attributable and revisable intent record;
- freeze the authority, rule, evidence, and time boundaries used by the run;
- decide which governed obligations and catalog techniques are applicable;
- select an effort tier from owned risk/effect policy, never model confidence;
- obtain provenance-bearing observations and discriminating challenges through a
  replayable actor protocol;
- reduce the finite registered rule set to exactly one typed evaluator outcome;
- record support, defeat, challenge closure, unresolved residue, and input
  digests in a reasoning receipt;
- distinguish historical replay from current-state revalidation; and
- make an effect impossible unless an independent exact-effect `CAV2-D37` gate
  passes for the same action, target, scope, and authority basis.

## Non-goals

- General-purpose truth discovery or proof of real-world truth.
- Automatic promotion of definitions, constitutions, schemas, rules, or claims.
- Model self-authorization, self-grading, or self-selected authority.
- Treating schema conformance as correctness, approval, or semantic evidence.
- A general actor runtime, real effect adapter, promoted engine contract, or
  executable ACI binding.
- A claim that challenges, diverse roles, or an `AntiBiasVector` cancel bias.
- Public mutation or publication of private DomainSpec/CAV2 material.

## Governed source contracts

| Source | Constraint carried into this candidate |
|---|---|
| `CAV2-D34` Authority | Applicability, owner routes, gates, and effects require explicit scoped authority. |
| `CAV2-D35` Provenance | Facts, rules, transformations, and receipts preserve typed source paths. |
| `CAV2-D36` Traceability | Intent must connect to inputs, judgments, effects, residue, and revision routes. |
| `CAV2-D37` Gate | Entry and exact-effect decisions retain full, distinct gate records. |
| `CAV2-D38` Claim <= proof | Outcome wording cannot exceed the captured support package. |
| `CAV2-D39` Intent | Source, purpose, scope, constraints, target pressure, output hypothesis, and revision route are the semantic minimum. |
| `CAV2-D40` Challenge Contract | Contestability names challenge modes, closure, owner review, and residue; it supplies no truth or confidence. |
| `CAV2-D41` Authority Model | Evidence, model output, validation, and repetition cannot silently become authority. |
| `CAV2-D56` Schema | Schema validation establishes admissible shape only. Population and interpretation are separate evidence operations. |
| Dispatch Technique Catalog | Techniques name route methods and checks; the catalog is not an evaluator or execution engine. |

Applicable constitutions may constrain a run only through a frozen authority
snapshot and rule manifest that names owner, scope, version, status, and
applicability. Quoting a constitution does not make it applicable, and a model
cannot decide its own governing obligations.

## Candidate system boundary

```text
IntentRecord --projection + revision trace--> ProblemFrame
                                                |
frozen AuthoritySnapshot + RuleCatalogManifest--+
                                                v
                              orchestration-entry GateDecision
                                                |
               TechniquePlan + EffortProfile----+
                                                v
                         bounded actor protocol + RuntimeJournal
                                                |
                                      ObservationSet
                                                |
                                                v
                             semantic-judgment evaluator@1
                                                |
                    ApplicabilityDecision + ReasoningReceipt
                                + evaluator outcome
                                                |
                                                v
                                  exact-effect GateDecision
                                                |
                                                v
                             idempotent effect attempt (future)
```

The evaluator request binds all frozen input digests; it does not retrieve or
silently complete missing authority, intent, evidence, method, or effort state.

| Boundary object | Enters through | Evaluator/receipt obligation |
|---|---|---|
| `IntentRecord` | traceable projection into `ProblemFrame` | Preserve intent and revision handles so a changed frame is detectable. |
| `AuthoritySnapshot` | frozen owner/source/status/temporal digest | Reject unauthorized, expired, revoked, or self-authorizing catalog state. |
| `ProblemFrame` | question, candidates, evidence handles, constraints, protected effects | Evaluate only the registered conclusion domain and expose missing handles. |
| `RuleCatalogManifest` | versioned rule/evaluator/challenge policy digest | Produce a reproducible `ApplicabilityDecision` before reduction. |
| `TechniquePlan` | owned method selection and stopping contract | Record executed technique versions and unmet required lanes. |
| `EffortProfile` | policy-derived tier, budget, escalation, and required roles | Record the applied profile without treating it as support strength. |
| `ObservationSet` | protocol-frozen typed observations and provenance | Admit or reject each observation under the manifest; do not copy facts into the frame. |
| `ApplicabilityDecision` | evaluator-produced intermediate record | Bind applied/defeated rules, conflicts, and owner residue into the receipt. |
| `ReasoningReceipt` + evaluator outcome | evaluator output | Bind derivation and residue; authorize nothing. |

These layers are non-substitutable:

- Gates own controlled transition decisions, not semantic inference.
- The actor protocol owns attempts, events, joins, timeouts, retries, and replay,
  not the conclusion.
- The evaluator owns only finite catalog applicability, reduction, defeat,
  abstention, and the semantic receipt.
- The effect boundary owns delivery of one exact authorized action, not a general
  permission inferred from the receipt.

## Witness invariant

An entry-gate verdict of `block` or `defer` produces zero actor and evaluator
calls. Entry `pass` permits only the bounded run named by that decision. No effect
occurs unless both conditions are true:

1. the evaluator returns `RecommendedUnderSnapshot`; and
2. the downstream exact-effect gate returns `pass` for the identical fixed effect
   envelope.

Every other evaluator outcome produces zero effect attempts. Repeat delivery of
the same positive fixed envelope may produce only one logical effect.

## Local candidate records

These names are implementation-planning handles, not canonical vocabulary.

| Record | Minimum responsibility | Boundary |
|---|---|---|
| `IntentRecord` | Preserve raw intent, the D39 semantic minimum, whole-field posture, accountable source attribution, and an explicit-or-unresolved revision route. | Not a command, requirement, scope approval, or canonical schema. |
| `AuthoritySnapshot` | Freeze owners, authority posture, governed sources, expiry, and revocation state. | Search or model output cannot add authority. |
| `ProblemFrame` | State question, candidates, evidence handles, boundary criteria, constraints, and protected effects. | Holds no facts and is not an accepted premise set. |
| `RuleCatalogManifest` | Name rules/evaluators, digests, issuers, precedence, challenge, temporal, and revocation policy. | Catalog membership does not self-authorize a rule. |
| `ApplicabilityDecision` | Record scope matches, conflicts, applicable obligations, and residue. | Must be reproducible under the snapshot. |
| `ObservationSet` | Hold typed, provenance-bearing facts and admissibility posture. | Schema-valid prose is not automatically admissible evidence. |
| `TechniquePlan` | Select actual Technique Catalog operations and required challenge roles. | Technique selection is method selection, not proof. |
| `EffortProfile` | Bind a policy-derived tier, budgets, required lanes, stop conditions, and escalation. | Effort never implies confidence or authority. |
| `ReasoningReceipt` | Bind inputs, versions, derivation, support, challenge, residue, and outcome. | Receipt is neither proof, approval, nor permission. |
| `RuntimeJournal` | Persist commands, events, attempts, joins, timeouts, replay, and closeout. | Historical replay emits no new model/tool call or effect. |
| `GateDecision` | Preserve complete entry or exact-effect D37 decision records. | Entry approval cannot authorize an effect. |

`ReasoningLane` remains omitted unless a fixture proves that it adds a distinct
operational or validation role not already represented by actor role, required
challenge, or technique.

## Evaluator outcome algebra

For one registered conclusion under one manifest and snapshot, the evaluator
returns exactly one terminal run outcome:

```text
InvalidInput
UnauthorizedCatalog
OutOfDomain
Ineligible.Defeated
Deferred.Insufficient
EscalateOwner
RecommendedUnderSnapshot
Invalidated
```

`RecommendedUnderSnapshot` means only that the registered conclusion follows
from the captured admissible observations under the named evaluator and catalog.
Unknown, missing support, unresolved ownership, an unclosed mandatory challenge,
catalog drift, expiry, or revocation cannot default to recommendation.

`InvalidInput`, `UnauthorizedCatalog`, and `OutOfDomain` are pre-reduction
terminal outcomes, not semantic judgments. The semantic judgment subset begins
only after input, catalog, domain, and applicability checks have admitted the
registered reduction.

## Constitutions, techniques, effort, and subagents

The four inputs play different roles:

1. **Constitutions and authority sources constrain.** Their frozen,
   owner-authorized obligations become candidate rules only through explicit
   applicability and provenance records.
2. **Technique Catalog methods operate.** A `TechniquePlan` selects concrete
   operations such as sequence, dialectic, tournament, validation loop, owner
   boundary check, and residue ledger because the current rule/effect policy
   requires them. Listing technique names without executing their checks is a
   validation flag.
3. **The effort controller budgets.** It chooses the minimum tier required by
   owned policy and effect risk. Removing evidence or required challenge lanes
   must never lower the tier or improve the semantic outcome.
4. **Subagents observe and challenge.** They return typed claims, source handles,
   counterexamples, or challenge receipts through the bounded protocol. Agent
   count and agreement do not increase authority. The evaluator—not the agents
   or their synthesizer—owns the catalog result.

The intended effort tiers are:

| Tier | Required shape | Maximum consequence before another gate |
|---|---|---|
| T0 | frame, sources, owner boundary, residue | read-only preflight or draft |
| T1 | one bounded analysis route with stopping/recomposition | narrow recommendation or draft |
| T2 | sequential explorer/auditor plus executable fixture validation | eligibility when required evidence lanes pass |
| T3 | distinct explorer/skeptic roles, declared join, convergence cap | recommendation plus challenge/residue |
| T4 | protected-action mapping, exact scopes, validation, effect gate | exact effect only after gate `pass` |

Unknown risk never selects T0/T1 by default. Missing owner, required evidence,
exact effect binding, or a resolvable material conflict blocks or defers.

## Anti-bias boundary

No `AntiBiasVector` participates in the first witness. The current repository
does not define governed bias dimensions, detection predicates, interventions,
aggregation semantics, or efficacy evidence. Naming a vector would therefore
turn an aspiration into pseudo-precision.

The candidate does support **contestability**: applicable challenge contracts,
named discriminating techniques, distinct roles where they add information,
grounded defeaters, counterfactual fixtures, and explicit residue. This can show
that a required challenge was run and handled. It cannot show that bias was
removed, cancelled, or independently measured.

## Functional requirements

| ID | Requirement |
|---|---|
| ARE-F01 | Preserve raw source intent beside its structured projection; keep technical capture provenance distinct from semantic source attribution, and never invent a revision owner. |
| ARE-F02 | Freeze all authority, catalog, evaluator, evidence, and temporal versions used by a run. |
| ARE-F03 | Decide applicability without allowing the model or evaluator to grant authority to its own inputs. |
| ARE-F04 | Derive effort and mandatory challenge lanes from owned policy/effect bindings. |
| ARE-F05 | Journal actor commands/events, attempts, joins, timeouts, and closure deterministically. |
| ARE-F06 | Return exactly one outcome from the stable evaluator-outcome algebra and abstain on insufficient support. |
| ARE-F07 | Record grounded support, defeaters, challenge closure, residue, and digests in a reasoning receipt. |
| ARE-F08 | Replay retained historical facts without re-running models, tools, or effects. |
| ARE-F09 | Revalidate separately against current authority/catalog/evidence state and invalidate drifted results. |
| ARE-F10 | Enforce zero effects for every non-positive outcome and require an exact-effect gate for a positive outcome. |
| ARE-F11 | Prevent schema validation, consensus, tokens, receipt existence, or test count from acting as authority evidence. |
| ARE-F12 | Keep private source material and candidate engine artifacts out of public Arcanum. |

## First witness acceptance family

`semantic-judgment evaluator@1` must register one conclusion and rule and vary
only the relevant evidence/catalog condition:

- supported facts -> `RecommendedUnderSnapshot`;
- required fact removed -> `Deferred.Insufficient`;
- grounded defeater added -> `Ineligible.Defeated`;
- required challenge timeout -> `Deferred.Insufficient`;
- irrelevant consensus added -> unchanged outcome;
- rule removed -> `OutOfDomain`;
- mutation, expiry, revocation, cyclicity, or self-judgment -> reject,
  invalidate, or escalate as specified.

A second independently authored rule family/frame must pass through unchanged
evaluator code. Effect and replay fixtures remain separate boundary witnesses.

### Bounded L0 evidence — 2026-07-23

The [terminal SWU-ARE-001 receipt](../../../implementation/agent-reasoning-engine/generated/runs/evaluator-v1-20260723T-session-001/TERMINAL-RECEIPT.json)
records one finite deterministic semantic relation, two independently owned rule
families, typed counterfactuals, byte-identical replay, persisted order, and a
test-only idempotent effect boundary. This witnesses the local evaluator slice
only. The explicit
[`G-ARE-L0` promotion receipt](../decisions/g-are-l0-promotion/PROMOTION-RECEIPT.json)
admits that bounded layer. A whole-engine runtime, real effects, ACI
compatibility, and anti-bias efficacy remain unproved.

## Open blockers and residue

1. **ACI integration disposition:** `G-ARE-ACI-BINDING` selected the
   ACI-subordinate target in
   [`BINDING-RECEIPT.json`](../decisions/aci-reasoning-binding/BINDING-RECEIPT.json).
   Integrated journal facts, canonical acceptance identity, replay cursor, and
   effect intents remain ACI-owned; semantic derivation stays evaluator-owned.
   External maturity and conformance remain open, so architectural selection is
   not runtime compatibility.
2. **Intent record residue:** g6 selected the local whole-field projection from
   admitted run 02. Revision-history item granularity, inter-rater consistency,
   representative fitness, and finer-grained provenance remain unwitnessed and
   cannot be promoted or silently completed.
3. **Artifact posture:** reasoning receipts and runtime journals remain local
   candidates until the artifact-admission owner decides their durability and
   canonical-kind route.
4. **Anti-bias claim:** blocked until a separate governed intervention and
   evidence program exists.

## Invoke define trace

- **Context Builder:** bounded to the confirmed dispatch, accepted research,
  active CAV2 definitions, and Technique Catalog; no public or canonical writes.
- **Interview/approval:** the operator confirmed the scoped package and one final
  Craft refresh subagent, then selected admitted run-02 option A at g6 after the
  rejected run-01 proposal was quarantined.
- **Template selection:** the implemented DomainSpec spec baseline was selected
  and locally adapted under the dispatch's three-file output contract. No tie or
  unsupported candidate-family creation was required.
- **Techniques used:** `sequence` orders accepted research, baseline definition,
  evidence experiment, reconciliation, design, and plan; `frame_handoff` exposes
  only bounded artifact handles to the experiment and design stages;
  `owner_boundary_check` prevents local records from claiming definition,
  constitution, evaluator, or effect authority; `artifact_contract_bridge` maps
  this baseline to later design and plan validations; `residue_ledger` preserves
  every unresolved owner question; and `scu_swu_reduction` selects
  `semantic-judgment evaluator@1` as the finite first witness that must recompose
  into the whole boundary.
- **Skipped obvious techniques:** `dialectic` and `tournament` are not used
  because this stage is not choosing among competing evaluator designs;
  `validation_loop` belongs to the evidence experiment and later witness; and
  `protected_action_mapping` belongs to the exact-effect design/plan boundary.
- **Dispatch validation:** the full route is
  [`../DISPATCH.json`](../DISPATCH.json), already validated before this stage.
- **Distill sanity check:** one bounded Proposer/Balancer validate pass initially
  flagged hidden input glue, frame/observation overlap, missing intent-to-frame
  trace, and algebra naming. The draft was revised with the explicit boundary
  mapping above. The whole-engine boundary is the meaning-preserving unit for
  definition; `semantic-judgment evaluator@1` is the smaller executable witness,
  and it recomposes only through frozen inputs, a bounded actor protocol, a
  `ReasoningReceipt`, and two non-collapsed D37 gate decisions. Design and
  plan—not define—own executable decomposition.
- **Frame expiry:** this optimization expires if owner-supplied applicability or
  challenge policy cannot be expressed as finite deterministic catalog input, or
  if the second independent rule family requires evaluator-code changes.
- **Layering:** deferred to plan with an explicit requirement for global L0-L3
  layering and `semantic-judgment evaluator@1` as the first SWU.

## Next route

Route `invoke:plan ACI-subordinate conformance revision`. The plan may
separate local-only evidence from future integrated conformance, but it must not
select or authorize an implementation SWU while external maturity and
task-specific gates remain open.

## Success boundary

This definition stage passes when the candidate boundary, non-substitution
rules, stable outcome algebra, witness invariant, effort limits, anti-bias
residue, and bounded first-witness claim are explicit. The local L0 evaluator
slice is witnessed; whole-engine implementation, promotion, effect,
ACI-compatibility, and reasoning-engine admission do not pass.
