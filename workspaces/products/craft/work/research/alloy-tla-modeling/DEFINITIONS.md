# Definition Cards

## Definition Card: Alloy Graph Completeness Model

Status: local-research-only

### Source Meaning

Alloy describes structures with constraints and the Analyzer finds satisfying structures or counterexamples within a bounded scope.

Source kind: primary-source plus operator-reading

Evidence: S2, S4, S5 in `SOURCE-RECORD.md`

### Formal Or Structural Shape

```text
DomainSpec graph
  -> signatures: Saga, Participant, Operation, Policy, Event, Interface, Mapping
  -> relations: orchestrates, triggers-cross, produces-for, enforces-cross, applies, maps
  -> assertions: missing compensation, missing participant owner, missing cross-context edge
  -> Alloy check within scope
  -> bounded counterexample or no counterexample in chosen scope
```

### Notation

| Symbol | Meaning | Shared notation link |
| --- | --- | --- |
| `sig` | set of atoms | `NOTATION-BRIDGE.md` |
| `check` | search for counterexample | `NOTATION-BRIDGE.md` |
| `for N` | finite scope | `NOTATION-BRIDGE.md` |

### Operator Reading

Alloy answers "can this shape exist while violating the graph obligation?" It is the right first formal target for DomainSpec relationship coverage.

### Use Carefully

- Always publish the scope with the result.
- Treat no-counterexample as "none found in this bounded scope."
- Use counterexamples as design feedback before mutating taxonomy or relationships.

### Misuse Warning

- Do not call graph completeness "saga correctness."
- Do not use Alloy as a hidden replacement for DomainSpec taxonomy governance.

### Promotion Boundary

promotion-candidate

## Definition Card: TLA+ Saga Execution Model

Status: local-research-only

### Source Meaning

TLA+ models systems as behaviors over states, with an initial condition and a next-state relation. TLC checks finite models; TLAPS is a separate proof system.

Source kind: primary-source plus operator-reading

Evidence: S7-S9 in `SOURCE-RECORD.md`

### Formal Or Structural Shape

```text
Saga execution
  -> variables: current step, completed operations, compensated operations, status, proof/evidence read markers
  -> Init: initial saga state
  -> Next: one forward, compensation, retry, dead-letter, or acceptance step
  -> invariants: success safety, failure safety, freshness rejection
  -> optional liveness: eventual terminal state under fairness assumptions
  -> TLC finite model check
```

### Notation

| Symbol | Meaning | Shared notation link |
| --- | --- | --- |
| `Init` | allowed first states | `NOTATION-BRIDGE.md` |
| `Next` | allowed transitions | `NOTATION-BRIDGE.md` |
| `[]P` | always property | `NOTATION-BRIDGE.md` |
| `<>P` | eventual property | `NOTATION-BRIDGE.md` |

### Operator Reading

TLA+ answers "is there an execution trace that violates the saga behavior obligation?" It is the right first formal target for temporal correctness.

### Use Carefully

- Separate safety invariants from liveness/fairness.
- Keep TLC finite-model results distinct from TLAPS proof claims.
- Bind model-check results to DCB freshness only when non-rerunnable evidence or acceptance races matter.

### Misuse Warning

- Do not generate TLA+ directly from prose without an intermediate fixture or extraction contract.
- Do not use TLA+ output as a UI or code-generation artifact.

### Promotion Boundary

promotion-candidate

## Definition Card: TypeScript Extraction And Bounded Witness Layer

Status: local-research-only

### Source Meaning

The existing `OrderFulfillmentSaga` toy harness checks a bounded graph witness, bounded behavioral assertions, and DCB freshness rejection in repo-local TypeScript.

Source kind: local-inference

Evidence: L3-L6 in `SOURCE-RECORD.md`

### Formal Or Structural Shape

```text
SagaSpec
  -> validateGraph(spec)
  -> enumerateRuns(spec, bound)
  -> assertBehavioralObligations(run)
  -> buildReadSet(result)
  -> AcceptSagaProofFreshnessClaim(readSet, currentFacts)
  -> optional generation of Alloy/TLA fixture inputs
```

### Notation

| Symbol | Meaning | Shared notation link |
| --- | --- | --- |
| `SagaSpec` | local TypeScript saga fixture shape | n/a |
| `AcceptSagaProofFreshnessClaim` | freshness acceptance command boundary | n/a |

### Operator Reading

TypeScript is the bridge from DomainSpec artifacts into formal-model fixtures. It gives fast local confidence and a data contract, but not proof.

### Use Carefully

- Keep result labels as bounded witness.
- Generate stable fixtures for Alloy/TLA instead of hand-copying facts each time.

### Misuse Warning

- Do not call the TypeScript result a formal proof.
- Do not let DCB acceptance freshness replace the behavior model.

### Promotion Boundary

borrow-carefully
