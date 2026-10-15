[Documentation home](../../README.md)

# Ledger

<a id="def-cal-definition-ledger"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Ledger

# Ledger

An ordered collection of identifiable entries with declared entry, integrity, correction, reconciliation and retention rules. It is not inherently append-only, true or authoritative.

**When it applies**

A Ledger is a governed ordered collection of independently identifiable entries maintained under an exact entry schema, ordering rule, integrity rule, correction policy, reconciliation procedure, owner, lifecycle, retention, and challenge contract.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Ledger does not imply append-only storage, event sourcing, accounting, truth, evidence acceptance, Decision authority, or one universal Ledger Artifact Type.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-ledger-section-2"></a>

## Source explanatory wording

A Ledger is a governed ordered collection of independently identifiable entries maintained under an exact entry schema, ordering rule, integrity rule, correction policy, reconciliation procedure, owner, lifecycle, retention, and challenge contract. Ledger does not imply append-only storage, event sourcing, accounting, truth, evidence acceptance, Decision authority, or one universal Ledger Artifact Type.

<a id="def-cal-definition-ledger-section-3"></a>

## Exact governing statement

A Ledger is a governed ordered collection of independently identifiable entries maintained under an exact entry schema, ordering rule, integrity rule, correction policy, reconciliation procedure, owner, lifecycle, retention, and challenge contract. Ledger does not imply append-only storage, event sourcing, accounting, truth, evidence acceptance, Decision authority, or one universal Ledger Artifact Type.

````
Ledger(x) => governed(x) and bounded(x); Ledger(x) =/=> authority_effect(x).
````

- Concrete Ledger kinds must declare whether entries are immutable, append-only, reversible, supersedable, or correctable.
- Ordering, identity, provenance, integrity, reconciliation, retention, and correction semantics are mandatory and cannot be inferred from storage technology.
- Append-Only Event Ledger is a specialization; Source-Ledgered Consolidation is a method that consumes source ledgers rather than a Ledger identity.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Definition specialization and resolution admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0014-definition-specialization-resolution/definitions/ledger/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.ledger@1.0.0-candidate.1

**Content fingerprint · SHA-256**

066e1fdbe724f5b627fbbcf87b9d323ed312d64db8d02cab247eadd282fd5db6

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Ledger is a governed ordered collection of independently identifiable entries maintained under an exact entry schema, ordering rule, integrity rule, correction policy, reconciliation procedure, owner, lifecycle, retention, and challenge contract.",
  "authority_scope_ref": "scope:ledger-definition",
  "exclusions": [
    "Ledger does not imply append-only storage, event sourcing, accounting, truth, evidence acceptance, Decision authority, or one universal Ledger Artifact Type.",
    "A database table, event history, log, register, Evidence Set, or list is a Ledger only when it satisfies an exact Ledger contract.",
    "This Definition does not admit a carrier, instance, relation, runtime, consumer, publication, or deployment."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
