[Documentation home](../../README.md)

# Traceability

<a id="def-cal-definition-traceability"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Traceability

# Traceability

The ability to follow explicit links between purpose, sources, decisions, changes, results and subsequent work.

**When it applies**

Use traceability when deciding whether CyberAlchemy v2 is navigable enough to resume, validate, publish, extract, or hand off. It is the check that source receipts, definitions, Craft state, decisions, and validation evidence are connected rather than merely present.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-traceability-section-2"></a>

## Source explanatory wording

Traceability means you can follow the thread from "why are we doing this?" to "what changed?" to "what happens next?"

<a id="def-cal-definition-traceability-section-3"></a>

## Exact governing statement

Traceability is the normalized definition identified by semantic.traceability, owned within scope.lineage, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D36 without silently merging it with another target.

Bound source-semantic basis:

Traceability is the ability to follow explicit, typed links across intent, source evidence, provenance, definitions, rules, methods, artifacts, gates, validation, decisions, residue, and next routes so that a later human or agent can answer why something exists, what it depends on, what it affects, and where to continue.

Traceability is satisfied only when the relevant chain has enough link targets, relation types, authority postures, and residue markers to be traversed without hidden conversation context.

````
For a work object `x` and a review question `q`, traceability holds when there
is a declared path:

```text
trace_q(x) = x -> link_1 -> link_2 -> ... -> answer_or_residue
```

Each `link_i` must have a target, relation type, and authority posture. If the
path breaks, the break must be recorded as typed residue or a named gap.
````

- Traceability is not the same as provenance. Provenance records origin and transformation history; traceability tests whether the project can navigate the relevant links for a question. Traceability is also not proof, completeness, or approval.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/traceability/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.traceability@1.0.0-candidate.1

**Content fingerprint · SHA-256**

3e2ec77affb54a73a7b6156112cad1e69dc298a92dd82ed7dc0e231dd0672c91

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use traceability when deciding whether CyberAlchemy v2 is navigable enough to\nresume, validate, publish, extract, or hand off. It is the check that source\nreceipts, definitions, Craft state, decisions, and validation evidence are\nconnected rather than merely present.",
  "authority_scope_ref": "scope.lineage",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
