[Documentation home](../../README.md)

# Root-Axis Independence Invariant

<a id="def-cal-definition-root-axis-independence-invariant"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Root-Axis Independence Invariant

Keeps separately governed dimensions—such as status, owner, representation and validation—independently variable unless an explicit rule relates them. Advancing one must not silently advance or authorize another.

**When it applies**

Use this invariant before merging or ordering concepts such as maturity and promotion, evidence confidence and owner commitment, schema residue and instance residue, role and lane, source evidence and local canon, built status and authority status, or workflow state and lifecycle status.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

Moving one slider should not secretly move another slider. If it does, name the wire between them.

## Exact governing statement

Root-Axis Independence Invariant is the normalized invariant identified by semantic.root-axis-independence-invariant, owned within scope.shared-authority, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D29 without silently merging it with another target.

Bound source-semantic basis:

Axis orthogonality invariant is the CyberAlchemy v2 rule that two authority-bearing dimensions, roles, states, owner lanes, schema or instance axes, validation concerns, or artifact properties are treated as independently variable unless an explicit typed relation, gate, schema rule, validator, or owner decision relates them.

Advancing one axis must not silently advance, validate, authorize, satisfy, or rewrite another axis. If a decision depends on such co-change, the dependency must be represented through `CAV2-D16` typed coupling invariant before it can govern work.

````
For a governed context `C`, let:

```text
A(C) = {a_1, a_2, ..., a_n}
```

be the declared axes that matter to a decision. Axes `a_i` and `a_j` are
orthogonal for decision `d` when a valid move on `a_i` does not imply a move on
`a_j` unless there is an explicit bridge:

```text
move(a_i) does not imply move(a_j) unless R_ij is declared
```

where `R_ij` is a typed coupling, gate, schema rule, validator, or owner
decision with named endpoints, direction or symmetry, evidence, and effect.
````

- Axis orthogonality is not isolation, not statistical independence unless a data model explicitly says so, not Hilbert-space or projector orthogonality, not a contextuality theorem, and not a consistency guarantee. It is a governance invariant about non-implied movement between axes. Interactions are allowed, but they must be explicit.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/root-axis-independence-invariant/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.root-axis-independence-invariant@1.0.0-candidate.1

**Content fingerprint · SHA-256**

3a95023cc9372a10a198815e04a94472847be688f8d564db5f1056df2167c308

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use this invariant before merging or ordering concepts such as maturity and\npromotion, evidence confidence and owner commitment, schema residue and\ninstance residue, role and lane, source evidence and local canon, built status\nand authority status, or workflow state and lifecycle status.\n\nWhen the question is whether a new label or classifier adds independent\ninformation, use `CAV2-D22` orthogonal classification. When the question is\nwhich authority lifecycle component changed, use `CAV2-D23` authority lifecycle\naxis. When the axes are not independent, use `CAV2-D16` typed coupling\ninvariant.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
