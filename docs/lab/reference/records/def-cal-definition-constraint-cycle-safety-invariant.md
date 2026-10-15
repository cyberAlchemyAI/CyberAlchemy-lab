[Documentation home](../../README.md)

# Constraint-Cycle Safety Invariant

<a id="def-cal-definition-constraint-cycle-safety-invariant"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Constraint-Cycle Safety Invariant

# Constraint-Cycle Safety Invariant

Forbids a connection from both constraining another subject’s values and participating in a cycle without an explicit acyclicity constraint. Proposals needing both properties must stop for schema governance and contextuality-obstruction review before influencing work.

**When it applies**

Use this guard when adding or revising ontology relations, relationship families, edge catalogs, movement edges, schema links, authority transitions, or validation-affecting graph rules. If the new edge can force a value or state and can also form cycles, block the promotion until the review names what constraints could fail to glue, what validator or reviewer will catch that failure, and which owner accepts the remaining residue.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-constraint-cycle-safety-invariant-section-2"></a>

## Source explanatory wording

An edge can either force a value or freely loop around the graph. If it does both, stop and prove the loop is safe before it becomes a rule.

<a id="def-cal-definition-constraint-cycle-safety-invariant-section-3"></a>

## Exact governing statement

Constraint-Cycle Safety Invariant is the normalized invariant identified by semantic.constraint-cycle-safety-invariant, owned within scope.shared-authority, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D28 without silently merging it with another target.

Bound source-semantic basis:

A value-cycle edge guard is the CyberAlchemy v2 invariant that no relation, edge type, or ontology movement may simultaneously:

- constrain the value, label, authority state, schema field, or validation outcome of another artifact; and - be allowed to participate in a cycle without an explicit acyclicity constraint.

If a proposed relation needs both properties, it must stop at schema governance and receive a contextuality-obstruction review before it can influence authority, ontology, validation, or implementation.

````
For any proposed edge type `E`, define two review predicates:

```text
value_constraining(E)
cycle_permitted(E)
```

CyberAlchemy v2 requires:

```text
not (value_constraining(E) and cycle_permitted(E))
```

unless a schema owner records an explicit exception with source evidence,
constraint semantics, satisfiability or obstruction review, validator or review
witness, and typed residue.

The current guard is a watch condition, not a theorem. It is satisfied when
value-constraining edges are acyclic and cycle-permitted edges do not constrain
values. It becomes live only when a proposed edge straddles both classes.
````

- Value-cycle edge guard is not a contextuality theorem, not a spectral-presheaf checker, not a ban on cyclic non-value relations, and not a ban on acyclic value constraints. It does not promote any live vault edge family. It only says which edge proposals must be stopped for schema governance and obstruction review.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/constraint-cycle-safety-invariant/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.constraint-cycle-safety-invariant@1.0.0-candidate.1

**Content fingerprint · SHA-256**

bf829b78c06764c34db536edd838cce4683716935ca0ec5bd9742f8d66e573fb

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use this guard when adding or revising ontology relations, relationship\nfamilies, edge catalogs, movement edges, schema links, authority transitions, or\nvalidation-affecting graph rules. If the new edge can force a value or state\nand can also form cycles, block the promotion until the review names what\nconstraints could fail to glue, what validator or reviewer will catch that\nfailure, and which owner accepts the remaining residue.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
