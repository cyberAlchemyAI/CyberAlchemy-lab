<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Ledger

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.ledger`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:ledger-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Ledger is a governed ordered collection of independently identifiable entries maintained under an exact entry schema, ordering rule, integrity rule, correction policy, reconciliation procedure, owner, lifecycle, retention, and challenge contract. Ledger does not imply append-only storage, event sourcing, accounting, truth, evidence acceptance, Decision authority, or one universal Ledger Artifact Type.

```text
Ledger(x) => governed(x) and bounded(x); Ledger(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Ledger contract. |

### Boundary conditions

- Concrete Ledger kinds must declare whether entries are immutable, append-only, reversible, supersedable, or correctable.
- Ordering, identity, provenance, integrity, reconciliation, retention, and correction semantics are mandatory and cannot be inferred from storage technology.
- Append-Only Event Ledger is a specialization; Source-Ledgered Consolidation is a method that consumes source ledgers rather than a Ledger identity.

### Testable conditions

- Every Ledger entry has a stable identity, schema, order position, provenance, integrity evidence, and lifecycle posture.
- Every correction follows the declared correction policy and preserves required history.
- Every Ledger exposes reconciliation and gap detection under its contract.
- No consumer infers truth, authority, or append-only behavior from the word Ledger alone.

## Plain-language voice

A Ledger is a governed ordered collection of independently identifiable entries maintained under an exact entry schema, ordering rule, integrity rule, correction policy, reconciliation procedure, owner, lifecycle, retention, and challenge contract. Ledger does not imply append-only storage, event sourcing, accounting, truth, evidence acceptance, Decision authority, or one universal Ledger Artifact Type.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

Ledger receives its own positive meaning so its carrier no longer borrows a broader Definition as its primary semantic identity.

### Examples

- ledger:ontology-semantic-events declares append-only complete-state events ordered by cursor, while ledger:artifact-inventory permits owner-reviewed corrective successor entries; both specialize the generic Ledger contract differently.

## Applicability

A Ledger is a governed ordered collection of independently identifiable entries maintained under an exact entry schema, ordering rule, integrity rule, correction policy, reconciliation procedure, owner, lifecycle, retention, and challenge contract.

### Exclusions

- Ledger does not imply append-only storage, event sourcing, accounting, truth, evidence acceptance, Decision authority, or one universal Ledger Artifact Type.
- A database table, event history, log, register, Evidence Set, or list is a Ledger only when it satisfies an exact Ledger contract.
- This Definition does not admit a carrier, instance, relation, runtime, consumer, publication, or deployment.

## Boundaries

- Concrete Ledger kinds must declare whether entries are immutable, append-only, reversible, supersedable, or correctable.
- Ordering, identity, provenance, integrity, reconciliation, retention, and correction semantics are mandatory and cannot be inferred from storage technology.
- Append-Only Event Ledger is a specialization; Source-Ledgered Consolidation is a method that consumes source ledgers rather than a Ledger identity.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.step3.gap | whole-file | `b4b19198b8671ef4d4ec22c6dd7b3125399652de92bf74aca8c2f71cd63ba5df` | `candidate-unadmitted` |

## Primary consumers

- CAL-DEFINITION-SPECIALIZATION-RESOLUTION-0014

## Lookup and drift

- Index: `authority/definitions/candidates/0014-definition-specialization-resolution/DEFINITIONS-INDEX.md` / `cal.definition.ledger@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0014-definition-specialization-resolution/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- .arcanum/ontology-vault/2026-10-06-lab-semantic-gap-audit.md

## Residue

- Definition-owner admission remains required.
- Artifact Type rebinding and admission remain separate.

## Claim ceiling

This candidate defines Ledger for Step 3 review only and has no admission or downstream activation effect.
