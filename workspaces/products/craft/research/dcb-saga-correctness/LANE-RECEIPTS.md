# DCB Saga Correctness Lane Receipts

Status: joined receipts
Date: 2026-06-15
Dispatch: `domainspec-v2-dcb-saga-correctness-research-20260615`
Join policy: parent synthesis

## Receipt Ledger

| Role | Agent | Status | Close | Reroute |
| --- | --- | --- | --- | --- |
| taxonomy-edge-mapper | `codex-taxonomy-edge-mapper-20260615` | completed | closed | none |
| dcb-boundary-advocate | `codex-dcb-boundary-advocate` | completed | closed | none |
| alternatives-challenger | `alternatives-challenger-20260615-001` | completed | closed | none |
| formal-modeler | `formal-modeler` | completed | closed | none |
| typescript-harness-builder | `codex-typescript-harness-builder` | completed | closed | none |

## Taxonomy Edge Mapper

Receipt:

```text
agent_id=codex-taxonomy-edge-mapper-20260615
role_id=taxonomy-edge-mapper
spawn_status=spawned
join_status=completed
close_status=closed
reroute=none
```

Key findings:

- The necessary concept set is mostly identified: `Saga`, `Workflow`,
  `Operation`, `Rule`, `Policy`, `Event`, `State Machine`, `Entity`,
  `Interface`, and `Mapping` are the saga proof vocabulary. Evidence:
  `TAXONOMY-EDGE-FRAME.md:30`, `arcanum/definitions/DEFINITIONS.md:130`.
- The frame's required edge set maps to existing relationship names:
  `produces-for`, `triggers-cross`, `enforces-cross`, `produces`,
  `transitions`, `applies`, `exposes`, and `maps`. Evidence:
  `TAXONOMY-EDGE-FRAME.md:45`,
  `arcanum/definitions/RELATIONSHIPS.md:13`.
- The main strained edge is `orchestrates`: the frame needs Saga to name
  coordinated operations, but `RELATIONSHIPS.md` types `orchestrates` as
  `Workflow -> Operation[]`, while Saga is distinct. Evidence:
  `TAXONOMY-EDGE-FRAME.md:49`,
  `arcanum/definitions/RELATIONSHIPS.md:140`,
  `arcanum/definitions/DEFINITIONS.md:202`.
- Compensation is under-modeled: DomainSpec says Saga has explicit
  compensation and rollback semantics, but the edge vocabulary has no
  `compensates`-style edge or ordered step edge. Evidence:
  `arcanum/definitions/TAXONOMY.md:222`, `TAXONOMY-EDGE-FRAME.md:63`,
  `implementation/domainspec/architecture/pattern-library/concepts/backend/saga.md:13`.
- Claim freshness needs a second vocabulary beyond the DomainSpec graph:
  `ModelCheckRunRecorded`, `ProofVerdictIssued`, `HumanWaiverApplied`,
  external receipts, and correctness claims. Evidence:
  `TAXONOMY-EDGE-FRAME.md:83`,
  `dcb-saga-correctness-research.dispatch.json:427`.

Gaps and tensions:

- `Participant` or bounded context is not a canonical meta-concept.
- `transitions` only points from `Event` to `State Machine`; proof needs
  from/to states, guards, effects, and invariants.
- The current vocabulary is good enough for graph coverage checks, but not
  enough by itself for temporal saga correctness or DCB-backed claim acceptance.

Handoff note:

Treat the taxonomy/edge frame as a useful coverage map, not proof-ready
vocabulary. Synthesis should mark `orchestrates`, compensation semantics,
participant representation, and evidence/claim freshness vocabulary as strained.

## DCB Boundary Advocate

Receipt:

```text
agent_id=codex-dcb-boundary-advocate
role_id=dcb-boundary-advocate
spawn_status=spawned
join_status=completed
close_status=closed
reroute=none
```

Key findings:

- DCB's strongest role is claim acceptance, not behavioral proof. Evidence:
  `TAXONOMY-EDGE-FRAME.md:17-28`.
- Saga correctness has real proof obligations outside DCB: participant
  boundaries, compensation completeness, guards, policies, event/state
  transitions, and success/failure safety. Evidence:
  `TAXONOMY-EDGE-FRAME.md:59-81`.
- The feasible DCB account is a read set and append condition around
  `SagaCorrectnessClaimAccepted`, especially over proof runs, waivers, external
  receipts, and model verdicts. Evidence: `TAXONOMY-EDGE-FRAME.md:83-108`.
- Prior DCB research narrowed DCB's value to non-rerunnable facts needing
  concurrency or causality. Evidence:
  `projects/domainspec-v2/research/dcb-correctness/RESEARCH-STRATEGY.md:23-33`,
  `projects/domainspec-v2/research/dcb-correctness/LANE-A-ALTERNATIVES.md:78-92`.
- The dispatch enforces the boundary: proof freshness and behavioral proof must
  remain distinct. Evidence: `dcb-saga-correctness-research.dispatch.json:427-431`,
  `dcb-saga-correctness-research.dispatch.json:483`.

Gaps and tensions:

- The raw phrase "using DCB to prove saga correctness" should be retired.
- The toy has candidate non-rerunnable facts, but no chosen hard case yet.
- Read marker semantics still need a per-dependency hash versus coarse rollup
  choice.

Handoff note:

Proceed with DCB as a freshness/concurrency wrapper around independently
produced saga proof evidence. Block any synthesis sentence that says DCB proves
saga behavior directly.

## Alternatives Challenger

Receipt:

```text
agent_id=alternatives-challenger-20260615-001
role_id=alternatives-challenger
spawn_status=spawned
join_status=completed
close_status=closed
reroute=none
```

Key findings:

- DCB is over-built when the question is behavioral saga correctness. Evidence:
  `TAXONOMY-EDGE-FRAME.md:19`,
  `dcb-saga-correctness-research.dispatch.json:427`.
- Most saga obligations are deterministic graph/model checks and should default
  to rerun-before-use, content hashes, or snapshot diff; only claim freshness is
  DCB-shaped. Evidence: `TAXONOMY-EDGE-FRAME.md:59`,
  `TAXONOMY-EDGE-FRAME.md:79`.
- Prior alternatives already narrow DCB to the residual hard class. Evidence:
  `projects/domainspec-v2/research/dcb-correctness/LANE-A-ALTERNATIVES.md:80`,
  `projects/domainspec-v2/research/dcb-correctness/HANDOFF.md:40`.
- The saga dispatch preserves the downgrade rule: the toy must include a
  non-rerunnable fact or concurrent race. Evidence:
  `dcb-saga-correctness-research.dispatch.json:434`,
  `dcb-saga-correctness-research.dispatch.json:331`.
- Certificate/version binding is cheaper for local verdict freshness, but TTL
  is unsound and multi-fact claims reintroduce read sets. Evidence:
  `projects/domainspec-v2/research/dcb-correctness/LANE-A-ALTERNATIVES.md:57`.

Gaps and tensions:

- The saga fact vocabulary does not yet classify deterministic/rerunnable facts
  versus non-rerunnable facts.
- A DCB-friendly toy may be biased if it injects a waiver only to justify DCB.

Handoff note:

Default to cheaper freshness mechanisms. Use DCB only for non-rerunnable saga
evidence or concurrent acceptance races, and keep behavioral proof owned by the
selected model or harness.

## Formal Modeler

Receipt:

```text
agent_id=formal-modeler
role_id=formal-modeler
spawn_status=spawned
join_status=completed
close_status=closed
reroute=none
```

Key findings:

- Best first fit for saga execution correctness is TLA+/PlusCal, with
  TypeScript as extractor/harness. Evidence: `TAXONOMY-EDGE-FRAME.md:19`,
  `TAXONOMY-EDGE-FRAME.md:147`.
- TypeScript alone should not count as proof; it is useful only as bounded
  witness or property-test harness. Evidence: `TAXONOMY-EDGE-FRAME.md:145`,
  `dcb-saga-correctness-research.dispatch.json:279`.
- Alloy is the best alternate if the first toy is graph completeness rather
  than execution behavior. Evidence: `TAXONOMY-EDGE-FRAME.md:149`,
  `arcanum/definitions/RELATIONSHIPS.md:15`.
- Lean should be deferred unless the theorem is deliberately small. Evidence:
  `TAXONOMY-EDGE-FRAME.md:151`,
  `dcb-saga-correctness-research.dispatch.json:282`.
- DomainSpec's saga shape is inherently temporal, and State Machine is the
  formal/testable lifecycle concept. Evidence:
  `arcanum/definitions/TAXONOMY.md:222`,
  `arcanum/definitions/TAXONOMY.md:306`.

Gaps and tensions:

- Repo fit points to TypeScript; proof signal points to TLA+/PlusCal or Alloy.
- "Saga correctness" mixes temporal execution correctness and typed-edge
  completeness.

Handoff note:

Recommend TypeScript DomainSpec extractor plus TLA+/PlusCal model for the first
saga-execution toy. Use Alloy if synthesis narrows the toy to graph
completeness. Defer Lean.

## TypeScript Harness Builder

Receipt:

```text
agent_id=codex-typescript-harness-builder
role_id=typescript-harness-builder
spawn_status=spawned
join_status=completed
close_status=closed
reroute=none
```

Key findings:

- DCB should not be the proof engine. Evidence:
  `TAXONOMY-EDGE-FRAME.md:17`, `TAXONOMY-EDGE-FRAME.md:27`.
- The smallest useful TypeScript DSL is a typed `SagaSpec` with participants,
  forward operations, compensation operations, policies/rules, events/state
  transitions, mappings, and edge triples. Evidence:
  `TAXONOMY-EDGE-FRAME.md:59`,
  `arcanum/definitions/RELATIONSHIPS.md:16`.
- TypeScript is already the starting bias only if it produces a bounded witness
  or property harness. Evidence: `TAXONOMY-EDGE-FRAME.md:141`,
  `dcb-saga-correctness-research.dispatch.json:277`.
- Local tooling supports small deterministic TypeScript harnesses through
  `vitest`, `tsx`, and `tsx --test`. Evidence:
  `implementation/domainspec/tools/test-derivation-engine/package.json:8`,
  `implementation/domainspec/backend/package.json:6`.
- The DCB toy earns its keep only with non-rerunnable evidence. Evidence:
  `TAXONOMY-EDGE-FRAME.md:135`,
  `projects/domainspec-v2/research/dcb-correctness/HANDOFF.md:48`.

Smallest harness:

```text
SagaSpec object
  -> validateGraph(spec)
  -> enumerateRuns(spec, bound)
  -> property assertions
  -> acceptClaim(readSetHash, currentFacts)
```

Gaps and tensions:

- TypeScript gives fastest repo fit, but it is a bounded witness, not a
  mathematical proof.
- Existing code-tag tools help structural checks; saga compensation semantics
  still need an executor/trace model.
- Full TLA+/Alloy should wait until the TypeScript witness reveals whether the
  hard part is temporal interleaving or relationship completeness.

Handoff note:

Use a TypeScript bounded enumerator first. Promote to TLA+/Alloy only after the
toy proves which obligation class needs more rigor.

