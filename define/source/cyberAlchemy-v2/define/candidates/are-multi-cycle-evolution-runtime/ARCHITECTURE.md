# ARE multi-cycle evolution runtime architecture

Status: candidate conceptual architecture  
Owner: CyberAlchemy v2 product owner plus Agent Reasoning Engine product-meaning owner  
Authority effect: none  
Definition source: [ARE-MULTI-CYCLE-EVOLUTION-RUNTIME-DEFINITION-PACK.v1-candidate.json](ARE-MULTI-CYCLE-EVOLUTION-RUNTIME-DEFINITION-PACK.v1-candidate.json)

## Purpose

This document describes a small ARE-native runtime through which an agent uses
versioned JSON commands while the runtime owns evolution-cycle state, generated
data, evidence, accounting, receipts, recovery, and navigation.

The runtime is multi-cycle. Benchmark-driven research is one cycle type. It is
not the definition of evolution as a whole, and its semantic lifecycle is not
embedded in the common kernel. Historical E0-E10 labels are import aliases, not
runtime identifiers.

This is a candidate conceptual architecture. It does not adopt an implementation
technology, authorize construction or migration, start a benchmark, enable a
provider, activate an engine version, or grant any other effect.

## Architectural decisions

1. Extend the existing ARE `evolution-runtime`; do not create a second competing
   product runtime.
2. Separate the common evolution kernel from independently versioned cycle
   definitions.
3. Derive cycle state from immutable definitions and accepted events. Never
   accept direct state assignment from an agent, adapter, worker, or status file.
4. Make the runtime the logical system of record for all non-secret data produced
   by a cycle.
5. Store immutable bytes by content identity while binding their meaning and
   admissibility separately for each cycle.
6. Emit a receipt for every command, including rejected commands.
7. Connect cycles only through typed, receipt-bound handoffs accepted by the
   receiving cycle.
8. Keep controlled upgrade separate from research and engine improvement so
   evidence cannot silently become activation authority.
9. Keep operational indexes disposable and make cycle state reconstructible
   from durable definitions, events, receipts, and artifacts.
10. Import historical evidence without rewriting its chronology, exposure,
    hashes, or prospective posture.

### Resolved candidate decisions

`DG-01` establishes one admission boundary: the user alone admits a new cycle
definition, a successor version, a compatibility-breaking revision, or removal
from the active registry. Validators may reject malformed or incompatible
candidates; they cannot approve them.

`DG-02` selects hybrid reconstructible storage: append-only event and receipt
ledgers, a global content-addressed artifact store, and a transactional SQLite
operational index that can be rebuilt from durable evidence.

`DG-02A` selects a space-first lifecycle. Small identity, receipt, hash,
accounting, decision, handoff, and archive metadata stays hot. Immutable bytes
are deduplicated globally, compressed while warm, and packed into verified cold
archives when terminal, unpinned, settled, and not needed immediately. Archive
is reversible storage movement; permanent evidence deletion requires a separate
user decision.

`DG-03` selects cycle-specific semantic validators. The kernel verifies command
shape, bytes, hashes, schemas, provenance, and validation receipts. Each
user-approved cycle definition pins versioned validators for its own artifact
roles and transition criteria. Validators fail closed, produce receipts, and
rerun during recovery. Agents and workers cannot declare evidence sufficient.

`DG-04` places all five cycle types in the initial registry scope:
`benchmark-research/v1`, `research-learning/v1`, `engine-improvement/v1`,
`interaction-learning/v1`, and `controlled-upgrade/v1`. Registry scope is not
admission or enablement: DG-01 still applies to each definition, and controlled
upgrade remains unable to activate anything until its separate authority and
isolation requirements pass.

`DG-05` limits the first legacy import to the evidence closure needed to
reconstruct the current GLM 8K ContextBench H-EN hypothesis and candidate as
`awaiting-validation` (historically E5), ready for its independent construction
review. It excludes the complete historical campaign,
ARE-DSH, older ContextBench branches, and the third benchmark. Original hashes,
paths, chronology, exposure status, accounting gaps, and retrospective posture
must remain unchanged.

`DG-07` isolates controlled-upgrade execution in a separate process and
credential domain. It may share the versioned JSON protocol and consume only
explicitly handed-off evidence. Research and improvement workers cannot access
activation credentials. Activation still requires explicit user authorization,
an exact predecessor and rollback target, a bounded canary, and a terminal
retain, rollback, or block receipt.

`BR-01` defines benchmark-research identity around one immutable improvement
objective rather than one implementation candidate. The objective binds the
feature or capability, goal, benchmark and cohort, metric policy, measured
baseline, success and falsification rules, and applicable constraints.
Candidate hypotheses and bounded attempts may vary inside that lifecycle; a
material objective change or untouched confirmation creates a linked successor
cycle.

`BR-02` gives every objective a prospectively frozen metric policy. Primary
metrics determine success through an explicit logical rule, guardrails block
success when their frozen limits are violated, and diagnostic metrics explain
results without changing the decision. Metric identity, direction, cohort,
aggregation, baseline, threshold or comparison rule, missing-data treatment,
and uncertainty treatment are part of the frozen policy.

`BR-03` keeps each hypothesis independently attributable inside its shared
objective cycle. A hypothesis may yield multiple candidate implementations,
experiments, and attempts. Evidence, accounting, freezes, execution identities,
exposure posture, and outcomes remain attributable to the relevant records;
cross-hypothesis reuse must be explicit.

`BR-04` replaces numeric benchmark stages with semantic command, event, and
state identifiers. Commands such as `diagnose` propose work, events such as
`diagnosis-recorded` preserve accepted facts, and states such as
`awaiting-hypothesis` are derived projections. E0-E10 remain only as aliases on
historical imports.

`BR-05` makes the cycle an iterative hypothesis portfolio guided by one
objective. It may accept as many admissible hypotheses as are useful within its
declared bounds, and each may generate multiple candidates and experiments.
These are records in the same lifecycle, not nested cycles or independent
lifecycle engines.

`BR-06` gives that open-ended portfolio deterministic bounds. A cycle is
`active` while useful admissible hypothesis work and resources remain, `paused`
when a temporary prerequisite blocks progress, `confirmation-required` when a
development result must move to an untouched successor, `completed` only when
the required evidence satisfies the frozen success rule without a guardrail
failure, `exhausted` when no admissible path or hard resource remains, and
`cancelled` only by the user.

`BR-07` permits agents and admitted research workers to propose hypotheses
through JSON while leaving admission to the runtime's cycle-bound validator.
Admission requires objective relevance, falsifiability, mechanism, falsifier,
novelty or revision lineage, testability, expected evidence and resource needs,
provenance, exposure posture, and leakage, safety, and prohibited-method checks.
An admitted hypothesis is merely eligible for prioritization and gains no
execution authority.

`BR-08` reuses the existing research-ontology execution split. The Research DAG
is a verified dependency projection with topological layers and an informational
frontier; it is not an executor. The Research Work Plan declares exact tasks,
owners, lanes, dependencies, completion criteria, and validator identities, and
event replay derives readiness. The agent chooses among derived-ready work; the
runtime checks revision, prerequisites, budgets, concurrency, effect gates, and
evidence-bound completion. The existing generic scheduler remains only a
whole-cycle serialization and trigger-replay guard.

`BR-09` requires each immutable objective to select one comparison-reference
mode: `absolute-target`, `frozen-baseline`, or `prospective-paired-control`.
The exact reference evidence and permitted claim language are frozen with the
mode. No mode is universal. The current GLM 8K ContextBench objective remains
candidate-only under `frozen-baseline`; historical controls are descriptive and
cannot establish a new matched efficiency claim.

`BR-10` freezes each experiment before measurement-bearing execution. The
freeze binds the hypothesis, candidate bytes, model settings, cohort, prompts,
metrics, sources, leakage policy, budgets, stop and retry rules, concurrency,
adapters, validators, and configuration. Executions are separate settled
attempts. A post-freeze change creates a content-addressed successor experiment;
failed and partial attempts and unknown costs remain visible.

`BR-11` derives hypothesis decisions from verified observations and experiment
evidence. The typed outcomes are `collect-replications`, `run-experiment`,
`revise-hypothesis`, `supported`, `rejected`, `inconclusive`, and `exhausted`.
Revision creates a successor, inconclusive continues only while an admissible
test remains, and legacy `candidate-supported` maps to `supported` without
rewriting its source evidence.

`BR-12` places execution inside one immutable, user-approved cycle envelope.
The envelope bounds providers, models, credential slots, data exposure,
experiment classes, calls, tokens, cost, time, concurrency, applicable network
and geography constraints, and expiry. Every frozen experiment still needs a
runtime launch-admission receipt proving that it fits the envelope and passes
its prerequisites. Admitted attempts and policy-frozen retries do not require
repeated user approval; anything outside the envelope blocks for a new user
decision. Freeze, validation, admission, lease, attempt, and settlement remain
separate records.

`BR-13` keeps deterministic validators as the normal path and adds conditional
independent-agent review. On failed or ambiguous validation, conflicting
observations, materially novel output, uncertain evidence or leakage, or a
claim-ceiling risk, the runtime creates a typed review task. It sends the exact
output and immutable evidence bundle to an agent distinct from the producer.
The evaluation agent returns a structured recommendation and validation
receipt; it cannot mutate state or grant authority. The runtime applies the
transition, and unresolved authority, envelope, or definition questions return
to the user.

`RL-01` identifies each research-learning cycle by one immutable bounded
research question, intended learning outcome, and declared use. Multiple
hypotheses, experiments, observations, and learning decisions may contribute to
that question without becoming child cycles. A material change to the question,
outcome, use, scope, or answerability criteria creates an explicitly linked
successor cycle.

`RL-02` derives the cycle-level question disposition from the complete verified
evidence portfolio. The typed dispositions are `answered`,
`partially-answered`, `inconclusive`, `exhausted`, and `invalidated`. Each
records confidence or evidence strength, counterevidence, limitations,
applicability, unresolved parts, and successor questions. A supported
hypothesis is contributing evidence and a technique candidate is an optional
handoff; neither automatically completes the question.

`RL-03` freezes an answerability contract before cycle admission. It declares
acceptable evidence and provenance quality, sufficiency and independence,
counterevidence handling, confidence semantics, applicability boundaries,
resource ceilings, and stop, exhaustion, and invalidation conditions. Evidence
may accumulate under that contract, but a material threshold change creates a
successor cycle rather than moving the rule after results are visible.

`RL-04` admits typed multimodal evidence under that contract: source analysis,
static inspection, verified artifacts, observation, reproduction, controlled
experiments, benchmark results, and structured evaluation-agent reviews. Each
item carries immutable provenance, quality and independence posture, temporal
scope, limitations, applicability, claim ceiling, and validation. Experiments
may be required by a question but are not universal to research learning.

`RL-05` exports an immutable Research Finding Bundle: question disposition,
hypothesis outcomes, evidence and counterevidence, uncertainty, limitations,
applicability, claim ceiling, successor questions, optional technique
candidates, provenance, and validation receipts. A receiving cycle explicitly
accepts the exact digest and selected claims. The bundle transfers no state,
budget, credentials, permission, or implementation authority.

`RL-06` reuses the Research Work Plan and DAG to derive readiness while leaving
task choice to the research agent. The runtime verifies revisions,
prerequisites, criteria, budgets, concurrency, effect policy, and leases, then
admits effectful work only inside a user-approved cycle execution envelope.
In-policy work does not require repeated approval; out-of-envelope work returns
to the user. Recovery replays events and resolves leases before redispatch.

`EI-01` identifies an engine-improvement cycle by one immutable measurable
objective binding accepted signals or findings, the exact engine surface,
desired behavior, primary and guardrail metrics, baseline, scope, prohibited
changes, resources, and stop bounds. Multiple techniques, attempts, and
content-addressed variants may compete beneath it. A material objective change
creates a successor cycle.

`EI-02` makes the cycle recommend-only. Verified evidence produces
`recommend-variant`, `reject-variant`, `revise-technique`,
`continue-comparison`, or `exhausted`. A recommendation binds exact variant and
baseline bytes, environment, comparisons, guardrails, limitations,
applicability, rollback requirements, evidence, and validation receipts. It may
be offered to controlled upgrade but cannot change active state itself.

`EI-03` constructs each variant in an isolated workspace outside the serving
checkout with an exact baseline, dependencies, toolchain, environment,
mutation allowlist, prohibited paths, technique binding, builder identity, and
one runtime-controlled writer lease. Measurement seals the complete bytes and
bindings into a content-addressed identity. Any later change creates a
successor variant, and evidence never transfers across identities.

`EI-04` freezes a staged comparison contract before results are visible. It
binds exact baseline and variants, screening, advancement, full repetitions,
guardrails, independent confirmation, aggregation, tie-breaking, selection,
budgets, retries, and stop conditions. Every branch and failure remains
visible. Only a variant passing every required stage may be recommended, and a
post-result contract change creates a successor comparison.

`EI-05` retains only an exact implemented-and-verified candidate bound to
selected implementation, configuration, objective, baseline, evidence,
validator, toolchain, limitation, and applicability digests. Currentness is
recomputed whenever reuse is considered. Any selected binding drift marks the
retention stale and returns the candidate to the experiment frontier while
preserving the historical record.

`EI-06` places construction and comparison inside one immutable user-approved
effect envelope. It bounds mutations, command classes, toolchains, builds,
tests, containers, network and providers, credentials, data exposure,
workspaces, calls, tokens, cost, time, concurrency, retries, recovery, and
expiry. The runtime issues separate construction and comparison admissions.
In-policy effects proceed without repeated approval; anything outside the
envelope returns to the user.

`IL-01` identifies an interaction-learning cycle by one immutable scoped
learning objective. It binds the attributed problem, subject and context,
participant or interaction cohort, desired behavior, success and guardrail
criteria, privacy, consent, retention and revocation, resources, and stop
conditions. Multiple lessons and assessed applications may contribute beneath
it; a material scope or privacy change creates a successor cycle.

`IL-02` admits only attributed, minimized, policy-eligible interaction evidence:
explicit corrections and approvals, observable task outcomes, deterministic
checks, and scoped application outcomes. Every item binds its scope, policy
basis, classification, redaction or minimization, retention, expiry, revocation,
limitations, and validator receipt. Raw interaction content is referenced or
minimally retained rather than copied wholesale by default. Hidden reasoning,
secrets, unauthorized third-party private content, unverified inference, and
model self-assessment are excluded; inferred preferences require attributable
validation and cannot silently generalize beyond their participant or cohort.

`IL-03` derives a lesson only when admitted evidence satisfies the objective's
declared sufficiency and guardrail criteria. Every application deterministically
matches subject, participant or cohort, context, purpose, privacy posture, and
validity interval; a current explicit user instruction always takes precedence.
Each attempt emits an outcome receipt, including policy or scope mismatch.
Expiry or revocation blocks new applications immediately. Historical receipts
remain evidence under their own retention rules, but reusable content cannot
survive the authority that permitted its retention.

`IL-04` classifies every application as confirmed, ineffective, harmful,
inconclusive, or not-applicable. The complete admitted portfolio derives a
lesson's candidate, supported, contested, suspended, revoked, or expired
standing; the latest result never erases earlier evidence. Success requires the
prospectively declared recurrence or replication threshold without a blocking
guardrail failure. The cycle terminates as achieved, partially-achieved,
exhausted, revoked, or superseded with the complete decision basis attached.

`IL-05` places evidence capture, retention, and live lesson application inside
an immutable user-approved effect envelope with runtime admission at the
capture/retention and application boundaries. Completion emits an immutable
Interaction Learning Bundle and may offer a non-authorizing improvement signal.
A receiving cycle must validate and accept the exact handoff under its own
definition and envelope; no lesson or bundle directly changes persistent
memory, prompts, policy, engine state, activation, release, or deployment.

`CU-01` keeps controlled-upgrade identity deliberately small. One immutable
Activation Binding names only the exact candidate, target serving environment
or slot, and current serving predecessor that is also the rollback point. The
recommendation remains linked evidence, and an owner-authorization receipt
binds the Activation Binding digest. Canary rules, budgets, schedules,
credentials, and other operational details remain separate records. Changing
candidate, target, or predecessor creates a successor cycle.

`CU-02` uses one human authorization boundary. After deterministic readiness
passes, the user approves the exact Activation Binding and its separately bound
execution policy. The isolated controller may activate, observe the bounded
canary, and retain or roll back without more approvals. Drift, out-of-policy
action, or indeterminate settlement blocks and returns to the user; emergency
rollback to the approved rollback point remains available without a new gate.

`CU-03` performs one minimal deterministic recheck immediately before serving
state changes: candidate bytes match, the target still serves the expected
predecessor, rollback remains available, and authorization plus policy remain
current. Any failure or unknown blocks activation. The switch itself compares
the predecessor atomically, so concurrent state drift produces a blocked
receipt rather than an overwrite.

`CU-04` freezes canary signals, thresholds, window, and deadline before
activation. Pass retains; failure, missing required evidence, or an
inconclusive result at deadline rolls back automatically. A verified rollback
settles the cycle without another human gate. An unverifiable rollback blocks,
preserves the observed state and evidence, and alerts the user rather than
claiming recovery. Every path emits a settlement receipt.

`CU-05` recovers by replaying the journal and then observing real serving
state. An active predecessor returns to the normal final readiness boundary; an
active candidate resumes the existing canary while policy is valid and rolls
back after expiry; any other or unverifiable state blocks. Stable operation
identities make recovery idempotent, and every reconciliation emits a receipt
without resetting observation windows or inferring retention.

`CR-01` derives three projection layers from one authoritative event chain:
aggregate objective-cycle disposition, subordinate record states, and
executable work states. Independent records and work may progress concurrently
while the objective remains active. Semantic operations target the appropriate
record or work item and recompute the affected views; none of the layers owns a
separate ledger or accepts direct status assignment.

`CR-02` places immutable envelope identity, bounded-effect and resource checks,
credential-slot references, data exposure, expiry, currentness, admission
receipts, deviations, and recovery in one kernel mechanism. Cycle definitions
supply their typed policy fields, validators, and named phases. Sharing the
mechanism does not merge policies or let an admission cross cycle, phase, or
binding boundaries.

These are user-approved candidate directions. They do not admit a cycle
definition or objective, select implementation bytes, or authorize migration.

## Existing baseline

The existing
[`implementation/agent-reasoning-engine/packages/evolution-runtime`](../../../implementation/agent-reasoning-engine/packages/evolution-runtime/README.md)
already provides bounded mechanisms for improvement signals, targets, research
records, technique candidates, reproduction trials, content-addressed variants,
comparisons, scheduling, benchmark registration, interaction learning, retained
improvements, and recommend-only upgrade decisions. It also includes optional
controlled-local activation and rollback behavior.

The current package is therefore a predecessor, not an empty directory. The
architectural change is to expose a stable common kernel and move workflow
meaning into explicit cycle definitions. Existing mechanisms can later be
mapped into those boundaries under a separately authorized implementation plan.

## Context view

```text
                   JSON command / JSON response
Agent or operator ──────────────────────────────────────┐
                                                        v
                                                +---------------+
Benchmark, review,                            | JSON protocol  |
or system adapter ───────────────────────────>| boundary       |
                                                +-------+-------+
                                                        |
                                                        v
  +-------------------------------------------------------------------+
  |                  ARE evolution kernel                              |
  | identity | revision | validation | transition | budget | receipts |
  +-----------+------------------------+----------------------+---------+
              |                        |                      |
              v                        v                      v
     +----------------+       +-------------------+   +----------------+
     | cycle-definition|       | managed evidence  |   | worker/lease   |
     | registry        |       | store             |   | boundary       |
     +----------------+       +-------------------+   +----------------+
              |                        |                      |
              v                        v                      v
     cycle-specific rules       immutable objects,       staged output,
     and state vocabulary       events and receipts      explicit settle
```

The agent is a caller. It is not the state store, transition engine, artifact
organizer, budget authority, or evidence verifier.

## Component responsibilities

### JSON protocol boundary

The boundary validates one command envelope before domain processing. The
minimal envelope contains:

```json
{
  "schema_version": "are.evolution-command/v1",
  "command_id": "globally-unique-id",
  "operation": "artifact.ingest",
  "cycle_id": "glm8k-contextbench-hen-r1",
  "expected_revision": 12,
  "payload": {}
}
```

`command_id` provides idempotency. `expected_revision` provides optimistic
concurrency. Repeating identical command bytes returns the same disposition;
reusing an identity with different bytes blocks.

The protocol accepts only declared operations. It is not a general shell,
arbitrary-code, or file-mutation interface.

### Cycle-definition registry

The registry resolves an immutable definition by `cycle_type`, schema version,
and definition digest. A definition declares:

- states and terminal outcomes;
- accepted commands and events;
- transition guards;
- evidence roles and validators;
- budget and concurrency policies;
- required owner gates;
- work-item and settlement shapes;
- admissible incoming and outgoing handoff types; and
- compatibility rules for successor definitions.

An existing cycle instance remains bound to its original definition digest.
Installing a successor definition never changes historical state semantics.

Only the user may admit a definition or successor into the active registry.
Merely placing a JSON file in a directory, passing validation, or receiving an
agent recommendation cannot admit a cycle type.

### Evolution kernel

The kernel provides mechanisms common to every cycle:

- command identity and schema validation;
- cycle and revision lookup;
- exact definition binding;
- optimistic concurrency and idempotent replay;
- transition evaluation;
- event creation and hash chaining;
- artifact-ingestion coordination;
- budget reservation and settlement;
- work-lease issuance and expiry;
- projection rebuilding;
- receipt creation;
- cross-cycle handoff validation; and
- verification and reconstruction export.

The kernel does not know that `awaiting-validation` requires an independent
construction review or that a canary failure requires rollback. Those meanings
belong to their cycle definitions.

### Managed evidence store

The evidence store is one logical boundary with distinct physical roles:

```text
Managed evidence store
├── immutable object store
│   └── content-addressed artifact bytes
├── append-only event ledger
│   └── accepted state-relevant facts
├── append-only receipt ledger
│   └── accepted and rejected command results
├── artifact catalog
│   └── cycle-scoped semantic bindings and provenance
├── state projections
│   └── reproducible current views
└── operational index
    └── disposable query, revision, lease, and budget acceleration
```

The architecture does not require large artifact bytes to live in a relational
database. It requires them to be ingested, content-identified, catalogued, and
reachable only through runtime-owned records.

Credentials, tokens, private keys, and other secrets are prohibited artifacts.
Provider request evidence must reference secret slots or redacted environment
bindings rather than persist secret values.

#### Space-first storage lifecycle

The selected logical tiers are:

```text
HOT   small metadata, current projections, active work and immediate evidence
  ↓
WARM  globally deduplicated and compressed immutable objects
  ↓
COLD  verified packed archives with hot manifests and restoration metadata
```

The runtime does not infer subjective importance. It uses explicit states:
`active`, `user-pinned`, `active-reference`, `terminal-unpinned`, `superseded`,
and `temporary`. Terminal unpinned data becomes archive-eligible only after its
work settles, validators complete, live leases and immediate dependencies clear,
the archive verifies, and a restoration check reproduces the original hashes.

Cycle reconstruction bundles remain logical manifests over the global object
store, avoiding per-cycle duplication. Automatic garbage collection is limited
to staging, caches, disposable projections and indexes, or objects proven to be
unreferenced. Permanent evidence deletion is a separate user gate.

### Artifact ingestion

A worker or adapter writes proposed output into runtime-controlled staging and
submits an ingestion command. The logical operation is:

1. Resolve the cycle and expected revision.
2. Read the staged bytes through the runtime boundary.
3. Reject prohibited content classes and undeclared artifact roles.
4. Compute content identity, byte length, and media type.
5. Validate any declared structural schema.
6. Materialize an immutable content object.
7. Create a cycle-scoped artifact binding.
8. Append the accepted event and receipt.
9. Recompute budgets, state, blockers, and next admissible operations.
10. Leave any unreferenced object as harmless residue until governed cleanup;
    never hide a partially committed state transition.

Semantic acceptance is separate from byte ingestion. For example, valid JSON
can be stored while still being rejected as insufficient construction-validation
evidence.

### Event and receipt ledgers

An accepted state-relevant command produces an immutable evolution event and a
receipt. A rejected command produces a receipt but no state-changing event.

Every receipt binds at least:

- command identity, operation, and digest;
- accepted, rejected, replayed, or blocked disposition;
- cycle identity, revision, type, and definition digest when applicable;
- state digest before and after;
- budget state before and after;
- referenced evidence and artifact digests;
- predecessor event and receipt digests where applicable;
- reason codes and blockers;
- runtime and schema version;
- authority effect; and
- receipt digest.

Receipt existence proves the bounded runtime decision only. It does not prove
that source claims are true, an owner had authority, a model answer is correct,
or an external effect completed.

### Projection and navigation service

Human-readable status is generated from durable records. It is never maintained
as a second authority source.

Required views include:

- current cycle state and blockers;
- complete cycle timeline;
- artifact inventory by role, state, attempt, producer, and digest;
- budget and accounting summary;
- active, expired, and settled work leases;
- incoming and outgoing handoffs;
- open questions and owner gates;
- verification status; and
- next admissible JSON operations.

These views can be rendered as JSON and optional Markdown. A stale Markdown
summary cannot change cycle state.

### Work and worker boundary

Cycle definitions may expose work items. A worker can execute an item only after
the kernel issues a dispatch lease that reserves the declared concurrency and
budget.

```text
ready work item
      |
      v
dispatch.acquire ──> lease ──> worker ──> staged outputs
                                             |
                                             v
                                    dispatch.settle
                                             |
                                             v
                              accounting + artifacts + receipt
```

Workers do not write the durable ledger. They do not set cycle state. Failure,
timeout, cancellation, retry, and unknown usage remain explicit settlement
outcomes rather than disappearing from the successful path.

### Cross-cycle handoff service

A handoff is a typed offer from one cycle to another. It contains the source
cycle and state digests, exact artifacts and receipts, output type, claim
ceiling, intended receiving cycle type, and acceptance status.

The receiving cycle decides whether the handoff satisfies one of its input
roles. Acceptance creates a receiving-cycle event and receipt. Rejection leaves
the source evidence unchanged.

No cycle may directly edit another cycle, share a mutable state object, or use a
foreign terminal status as its own transition.

## Cycle taxonomy

### Benchmark research

Purpose: determine whether candidate hypotheses improve one immutable objective
under a prospectively fixed benchmark contract, while preserving a
reconstructible scientific and accounting record.

The improvement objective is the identity and guide for the lifecycle. It
binds what feature or capability is being improved, the desired goal, benchmark
and cohort, metric policy, measured baseline, success and falsification rules,
and resource, quality, leakage, and operating constraints. Candidate approaches
such as H-EN and H-MC are hypotheses within that objective, not cycle identities.
Material objective changes create linked successor cycles; untouched
confirmation also runs as a successor so the original evidence remains frozen.

The metric policy assigns every measure exactly one role. Primary metrics decide
success under a declared prospective logical rule. Guardrails can prevent a
success decision when a frozen limit is violated. Diagnostics may explain the
mechanism or result but cannot be promoted into decision criteria after results
are visible.

Candidate hypotheses accumulate beneath the objective:

```text
immutable improvement objective
├── H-EN hypothesis
│   └── candidates -> experiments -> attempts -> evidence and outcomes
├── H-MC hypothesis
│   └── candidates -> experiments -> attempts -> evidence and outcomes
└── cycle state, aggregate limits, and objective decision
```

The cycle may add further hypotheses while it remains active. Every candidate,
experiment, attempt, cost, freeze, and result stays attributable to its
hypothesis. Evidence reused across hypotheses is an explicit provenance link
whose exposure classification remains visible.

The semantic operations include `recover`, `diagnose`, `hypothesize`,
`specify`, `construct`, `validate`, `qualify`, `freeze`, `execute`, `evaluate`,
and `decide`. Under CR-01, each command addresses an exact subordinate record
or work item and then recomputes the aggregate objective disposition where
relevant. Each accepted command emits a distinct past-tense event, and callers
cannot assign any projection directly. E0-E10 may be shown beside imported
historical records only.

Hypothesis decisions use `collect-replications`, `run-experiment`,
`revise-hypothesis`, `supported`, `rejected`, `inconclusive`, and `exhausted`.
The objective cycle dispositions are `active`, `paused`, `completed`,
`confirmation-required`, `exhausted`, and `cancelled`. A result may create a
typed benchmark finding or improvement signal for another cycle. It cannot
activate an engine version.

ContextBench, ARE-DSH, and other benchmarks are adapters under this cycle type.
They may have different task formats and metrics while sharing the cycle's
research-integrity semantics.

### Research learning

Purpose: resolve a bounded uncertainty through falsifiable learning records.

```text
Question -> Hypothesis -> Experiment -> Observation
         -> Learning decision -> optional successor question
```

This cycle can consume benchmark evidence without owning benchmark dispatch. It
can offer a technique candidate or further research question to engine
improvement.

### Engine improvement

Purpose: create and compare an isolated engine variant against a measurable
target.

```text
Improvement signals -> Target -> Technique candidates
 -> Reproduction -> Engine variants -> Comparison
 -> Recommend or reject
```

This cycle specializes the earlier monolithic ARE EvolutionCycle and ends at a
recommendation boundary. It cannot activate the serving engine.

### Interaction learning

Purpose: preserve bounded lessons from observed interaction outcomes.

```text
Understanding assessment -> Scoped lesson -> Lesson application
 -> Application assessment -> optional improvement signal
```

Scope and counterevidence travel with the lesson. An interaction preference is
not generalized globally merely because it helped once.

### Controlled upgrade

Purpose: govern the different-risk boundary between recommendation and active
serving selection.

```text
Recommendation -> Owner authorization -> Exact predecessor binding
 -> Activation -> Canary -> Retain | Rollback | Block
```

This cycle runs with the separate process and credential isolation selected by
DG-07. Its owner
authorization cannot be inferred from benchmark results, comparison outcomes,
receipts, or model consensus.

## Composition model

```text
Interaction-learning ── improvement signal ──┐
                                             |
Research-learning ── technique candidate ────+──> Engine-improvement
                                             |             |
Benchmark research ── validated finding ─────┘             |
                                                           v
                                                upgrade recommendation
                                                           |
                                                           v
                                                  Controlled-upgrade
```

This diagram shows permitted typed flows, not automatic transitions. Every arrow
requires a handoff offered by the source cycle and explicitly accepted by the
receiving cycle.

An Evolution Program may group these cycle instances around one product intent,
but the program never merges their state, budgets, evidence admissibility, or
authority.

## Logical data model

```text
EvolutionProgram 1 ─── * CycleInstance
CycleDefinition  1 ─── * CycleInstance
CycleInstance    1 ─── * EvolutionEvent
CycleInstance    1 ─── * EvolutionReceipt
CycleInstance    1 ─── * ArtifactBinding * ─── 1 EvidenceArtifact
CycleInstance    1 ─── * BudgetAccount
CycleInstance    1 ─── * WorkItem 1 ─── * DispatchLease
DispatchLease    1 ─── 0..1 WorkSettlement
CycleInstance    1 ─── * CrossCycleHandoff
```

The content object is globally deduplicable. Artifact bindings, evidence roles,
validators, and admissibility remain cycle-scoped.

## JSON operation families

The candidate protocol needs the following operation families, not necessarily
one endpoint per line:

| Family | Purpose |
| --- | --- |
| `program.*` | Create and inspect non-executing groups of related cycles. |
| `cycle.create` | Bind one admitted definition to one new cycle instance. |
| `cycle.inspect` | Return the current reproducible projection. |
| `cycle.timeline` | Return ordered events and receipts. |
| `artifact.ingest` | Ingest staged bytes and create a cycle binding. |
| `artifact.list` | Query cycle-scoped artifact bindings. |
| `dispatch.acquire` | Reserve an eligible work item, budget, and concurrency slot. |
| `dispatch.settle` | Record terminal work output, failures, and accounting. |
| `decision.record` | Record a cycle-defined owner decision without bypassing guards. |
| `handoff.offer` | Create a typed outgoing handoff. |
| `handoff.accept` | Evaluate and accept or reject an incoming handoff. |
| `receipt.verify` | Verify one receipt and its bound dependencies. |
| `store.verify` | Verify ledger chains, object identities, and bindings. |
| `index.rebuild` | Rebuild disposable operational indexes. |
| `cycle.export` | Produce a reconstruction bundle. |
| `legacy.import` | Import historical material under a declared import policy. |

Every command returns a JSON receipt plus the current or unchanged revision,
blockers, and next admissible operation shapes.

## Transition evaluation

For a state-relevant command, the kernel conceptually performs:

1. Validate the command envelope and operation schema.
2. Resolve idempotency and reject conflicting command reuse.
3. Resolve the cycle and exact definition digest.
4. Compare `expected_revision` with the current revision.
5. Verify referenced artifacts, receipts, owner-gate records, leases, and
   budgets.
6. Evaluate the cycle-specific transition rule.
7. Construct the proposed event and next state projection.
8. Persist immutable evidence and event records under the durability contract.
9. Update or rebuild the operational index.
10. Emit the receipt and next admissible operations.

Failure at any step returns a reason-coded rejection receipt and leaves the
cycle revision unchanged.

## Evidence organization

The logical namespace is:

```text
runtime
├── definitions/<cycle-type>/<version>/<digest>
├── objects/sha256/<digest>
├── programs/<program-id>/projection
├── cycles/<cycle-id>
│   ├── identity
│   ├── events
│   ├── receipts
│   ├── artifact-bindings
│   ├── budgets
│   ├── work
│   ├── handoffs
│   └── projection
└── exports/<bundle-id>
```

This is a logical layout, not an adopted filesystem contract. Physical storage
may differ if it preserves the same identities, reconstruction property, and
authority boundaries.

## Reconstruction and recovery

The runtime must be able to recover without external calls:

1. Verify the selected cycle definition digest.
2. Verify the event and receipt chains.
3. Verify every required content object and artifact binding.
4. Replay events through the bound definition.
5. Recompute budget accounts, leases, blockers, and state.
6. Compare the rebuilt projection digest with any stored projection.
7. Rebuild the operational index.
8. Report orphaned objects, expired leases, incomplete settlements, or missing
   evidence as residue rather than hiding them.

A reconstruction bundle contains the closure needed for these steps without the
disposable index. It does not repeat provider calls or reproduce claims that
depend on unavailable external state.

## Legacy evidence

Existing benchmark directories remain evidence and must not be destructively
moved during definition or architecture work. A future import operation should:

- bind original paths and byte digests;
- record whether evidence was prospective, retrospective, exposed, holdout, or
  unknown;
- retain original timestamps only as source claims;
- create an import receipt at the actual import time;
- refuse to synthesize missing costs, receipts, or chronology;
- deduplicate identical bytes without collapsing semantic bindings; and
- expose unresolved classification as explicit residue.

The first intended import is the current GLM 8K ContextBench H-EN branch. Its
runtime projection should show the verified repaired construction evidence and
the independent-review frontier without implying that the historical work ran
inside the new runtime.

## Authority and safety boundaries

- JSON validity is not evidence validity.
- Evidence validity is not scientific acceptance.
- Scientific acceptance is not product acceptance.
- Product acceptance is not effect authorization.
- Receipt existence is not proof of external completion.
- A worker identity is not an independent-review guarantee by itself.
- A budget reservation is not settled usage.
- Unknown usage cannot silently become zero.
- A cross-cycle handoff is not a state transfer.
- A cycle definition cannot grant its own admission.
- Controlled upgrade requires its separately owned authorization boundary.
- No stored artifact may contain provider credentials or other secrets.

## Architectural acceptance conditions

A later design or implementation can claim conformance to this candidate only
if evidence shows that:

1. two cycle definitions with different state vocabularies can run concurrently
   without sharing mutable state;
2. direct state assignment is impossible through the public JSON protocol;
3. accepted and rejected commands both produce verifiable receipts;
4. a stale expected revision fails without changing state;
5. identical command replay is idempotent and conflicting replay blocks;
6. artifact bytes are immutable and their semantic bindings remain cycle-scoped;
7. failed, cancelled, timed-out, and unknown-cost work settlements remain in
   accounting;
8. the operational index can be deleted and rebuilt from durable evidence;
9. one cycle can offer a handoff that another cycle may accept or reject without
   mutating the source;
10. an engine-improvement recommendation cannot bypass controlled-upgrade
    authorization;
11. legacy import preserves original hashes and retrospective posture; and
12. one reconstruction bundle can reproduce the exported cycle state without
    provider access.

These conditions are architectural checks, not proof that an implementation
exists or is accepted.

## Open Questions

### Cross-cycle readiness review

The user selected NX-01 and the bounded review ran before implementation
planning. The predecessor evolution-runtime passed all 54 existing tests. The
review found the five cycle identities, typed non-authorizing handoffs, managed
evidence model, recovery model, and authority separations mutually compatible.

CR-01 resolves the state-ownership ambiguity with three projections derived
from one event chain. CR-02 projects the repeated benchmark, research, engine,
interaction, and upgrade envelopes onto one shared kernel mechanism with
cycle-specific policy, avoiding five separate security-critical
implementations. The existing controlled-local upgrade code is predecessor
evidence, not conformance to CU-01 through CU-05.

The cross-cycle architecture gates DG-01 through DG-07 are closed. The
per-cycle definition audit is now active. BR-01 through BR-13 close the
currently identified benchmark-research definition gates. RL-01 establishes
question-bound research-learning identity and RL-02 establishes typed,
evidence-derived question dispositions. RL-03 freezes the answerability
contract prospectively, RL-04 admits typed multimodal evidence, and RL-05
defines the cycle's cross-cycle handoff. RL-06 closes the currently identified
research-learning gates with derived readiness, agent task selection, and
runtime launch admission. EI-01 establishes measurable-objective identity for
engine improvement and EI-02 establishes its recommend-only decisions. EI-03
establishes variant isolation, identity, and mutation boundaries, and EI-04
establishes prospective portfolio comparison and selection. EI-05 establishes
exact retention with recomputed currentness, and EI-06 closes the currently
identified engine-improvement gates with separate bounded construction and
comparison admissions. IL-01 establishes scoped-objective identity, IL-02
establishes attributed, minimized, policy-eligible interaction evidence, and
IL-03 establishes evidence-supported lessons with scope-matched application.
IL-04 establishes typed application outcomes, portfolio-derived lesson
standing, bounded recurrence, and terminal dispositions. IL-05 establishes the
bounded operating envelope and non-authorizing handoff, closing the currently
identified interaction-learning gates. CU-01 establishes minimal immutable
controlled-upgrade identity. CU-02 establishes one exact approval with bounded
settlement and minimal human coordination. CU-03 establishes a final
deterministic readiness recheck and atomic predecessor comparison. CU-04
establishes frozen, fail-closed canary settlement. CU-05 establishes
deterministic, idempotent interruption recovery, closing the currently
identified controlled-upgrade and per-cycle definition gates.

NX-01, CR-01, and CR-02 are resolved. The cross-cycle semantic review is
complete. The user selected NX-02 option A, so the architecture moved into the
separately routed candidate implementation plan at
`goals/projects/agent-reasoning-engine/plans/multi-cycle-evolution-runtime/`.
That transition grants no planning admission or implementation authority.
Exact schemas, validators, storage layout, and migration remain downstream
phase-local planning and construction questions.

Exact cycle schemas, validator implementations, archive codec and pack format,
the H-EN file manifest, and the isolated controlled-upgrade process protocol
remain downstream design questions. They do not reopen DG-01 through DG-07
unless their evidence contradicts a selected boundary.

These questions are owned in the Definition Pack. They block the affected
downstream decisions but do not invalidate this candidate conceptual boundary.

## Claim ceiling

This document defines a candidate conceptual architecture. It does not promote
definitions, adopt a product capability, admit a cycle definition, bind an
implementation, migrate evidence, launch a benchmark, make provider calls,
activate an engine version, publish, release, deploy, or authorize an external
effect.
