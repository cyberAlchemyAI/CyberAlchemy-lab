# DCB Saga Correctness Research Lanes

Status: draft lane map
Date: 2026-06-15
Owner surface: DomainSpec v2 research

## Research Question

Can Dynamic Consistency Boundaries help DomainSpec prove or safely accept saga
correctness claims using the DomainSpec taxonomy and relationship vocabulary?

Important split:

- A formal model or executable harness proves properties of a saga.
- DCB guards whether a proof, validator verdict, waiver, or review claim is
  still fresh against the facts it read.

DCB should not be treated as the proof engine by itself. Its likely value is
preventing stale or racing acceptance of saga-correctness evidence.

## Source Vocabulary

Primary DomainSpec sources:

- `arcanum/definitions/TAXONOMY.md`
- `arcanum/definitions/RELATIONSHIPS.md`

Relevant meta-concepts:

- `Saga`: cross-feature transactional orchestration with compensation.
- `Workflow`: same-feature orchestration baseline.
- `Operation`: forward and compensation actions.
- `Rule`: preconditions, guards, and invariants.
- `Policy`: retry, dead-letter, timeout, and compensation selection.
- `Event`: cross-context signals.
- `State Machine`: participant and saga lifecycle states.
- `Entity`: state owners affected by forward and compensation operations.
- `Interface` and `Mapping`: boundary calls and data transforms.

Relevant edges:

- `orchestrates`: Saga or Workflow to Operations.
- `triggers-cross`: Event in one context activates Operation in another.
- `produces-for`: Operation in one context mutates or projects foreign state.
- `enforces-cross`: Rule in one context constrains another context operation.
- `produces`: Operation emits Event.
- `transitions`: Event changes a State Machine.
- `applies`: Policy governs Operation behavior.
- `maps` and `exposes`: boundary data and callable interfaces.

## Proposed Lanes

### Lane 1: Taxonomy and Edge Obligations

Question: What does DomainSpec already require a saga to name before any proof
is meaningful?

Output:

- Minimum saga proof-obligation catalog.
- Mapping from taxonomy concepts and relationship edges to proof obligations.

Candidate obligations:

- Every forward step has an owning bounded context.
- Every cross-context step has a typed edge.
- Every compensatable forward operation has a compensation operation or a named
  terminal failure policy.
- Events that advance saga state are connected to participant state machines.
- Cross-context rules are represented as `enforces-cross`, not hidden in prose.

### Lane 2: DCB Feasibility and Boundary Semantics

Question: Which saga-correctness facts need DCB-style freshness or concurrency
protection, and which facts should simply be recomputed?

Output:

- DCB fact vocabulary for saga correctness.
- Read-set and invalidation model for accepting a saga-correctness claim.
- Split between deterministic rerun-before-use facts and non-rerunnable facts.

Likely DCB facts:

- `SagaDeclared`
- `SagaStepDeclared`
- `CompensationDeclared`
- `CrossContextEdgeDeclared`
- `ParticipantStateMachineObserved`
- `RuleGuardObserved`
- `ProofVerdictIssued`
- `ModelCheckRunRecorded`
- `HumanWaiverApplied`
- `SagaCorrectnessClaimProposed`
- `SagaCorrectnessClaimAccepted`
- `SagaCorrectnessClaimRejected`

### Lane 3: Formal Model Language Tournament

Question: Which prebuilt structure gives the strongest proof signal for the
least ceremony?

Candidates:

- TypeScript with a small DomainSpec saga DSL plus property tests. Best for
  repo fit, extraction, examples, and developer adoption. Weak as a formal proof
  unless paired with model checking or exhaustive bounded search.
- TLA+ or PlusCal. Best for async saga protocols, compensation, retries,
  crashes, and temporal invariants. Higher learning cost, but a strong fit for
  correctness claims.
- Alloy. Best for relationship graph constraints over taxonomy and edge
  completeness. Less natural for long-running temporal behavior.
- Lean. Best for machine-checked theorem statements, but likely too heavy for
  first feasibility unless the proof target is narrowed aggressively.

Recommended starting shape:

- Use TypeScript as the extraction and toy harness language.
- Use TLA+ or Alloy as the formal witness lane, depending on whether the first
  toy focuses on temporal behavior or graph completeness.

### Lane 4: Executable Toy Saga

Question: Can we build one small saga where the DomainSpec graph yields proof
obligations and a stale correctness claim is rejected?

Toy candidate:

- `OrderFulfillmentSaga`
- Participants: ordering, payment, inventory, shipping.
- Forward operations: create order, authorize payment, reserve inventory,
  create shipment.
- Compensation operations: cancel order, void payment, release inventory,
  cancel shipment.
- Policies: retry, timeout, dead-letter, compensation ordering.

Expected proof targets:

- Safety: no accepted success state unless all required participant success
  states hold.
- Compensation: if a later participant fails, completed compensatable steps are
  either compensated or explicitly terminal.
- Boundary completeness: every cross-context activation and write-back has a
  DomainSpec edge.
- Freshness: a saga-correctness claim is rejected if any read saga step, rule,
  edge, model-check result, or waiver changed after its read marker.

### Lane 5: Alternatives and Cost Check

Question: When is DCB over-built compared with hash invalidation, rerun-before-
use, snapshot-diff, or certificate/version binding?

Output:

- Decision table for when to use DCB.
- Stop condition if TypeScript plus rerun-before-use proves sufficient.

Expected answer:

- Use rerun-before-use for deterministic validators and generated projections.
- Use content hashes for cheap dependency freshness.
- Use DCB only when the claim includes non-rerunnable evidence, concurrent
  promotion races, human/agent verdicts, external receipts, or causal ordering.

## First Feasibility Verdict Shape

The research should end with one of these:

- `promotion-candidate`: DCB is useful for accepting saga proof evidence.
- `borrow-carefully`: TypeScript or formal model works, but DCB is only a
  freshness wrapper.
- `analogy-only`: DCB helps language but not proof machinery.
- `block`: Saga correctness cannot be proven from current DomainSpec surfaces
  without adding missing taxonomy or edge requirements.

