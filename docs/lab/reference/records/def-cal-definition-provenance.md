[Documentation home](../../README.md)

# Provenance

<a id="def-cal-definition-provenance"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Provenance

# Provenance

A traceable account of where information came from, who or what produced it and the transformations and versions involved.

**When it applies**

When tracing an item to its sources, transformations and integrity boundaries.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Trace the omission claim to S1, E12, the account and filters, method version 2 and the saved comparison.

**Common mistake**

Treating traceability as proof of the cause or permission to act.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-provenance-section-2"></a>

## Source explanatory wording

Provenance is the receipt trail for where something came from and how it got here.

<a id="def-cal-definition-provenance-section-3"></a>

## Exact governing statement

Provenance is the normalized definition identified by semantic.provenance, owned within scope.lineage, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D35 without silently merging it with another target.

Bound source-semantic basis:

Provenance is the declared origin and transformation chain for a term, artifact, claim, rule, decision, relation, validation result, or residue. It records where the object came from, which sources or prior objects it depends on, which operations changed it, which owners or processes handled it, and which authority posture it held at each relevant step.

Provenance must identify source references and relation types with enough precision that a later reviewer can distinguish source evidence, local adaptation, promotion, demotion, translation, derivation, validation, and generated projection.

````
For object `x`, provenance is a typed path:

```text
Prov(x) = [(source_i, relation_i, operation_i, owner_i, posture_i)]*
```

The path may be incomplete only if the missing segment is explicitly recorded
as residue with an owner route. Untyped "came from" language is not sufficient
for authority-bearing use.
````

- Provenance is not proof, not authority, not trust, not validation, and not credit assignment by itself. A perfect source trail can still point to a false, unpromoted, private, or unusable claim. It only tells the project where meaning and transformations came from.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/provenance/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.provenance@1.0.0-candidate.1

**Content fingerprint · SHA-256**

514e2c9e19882553cbdfb1f10b94dacb510bf010a9aa0727b1068aff839ca86b

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use provenance before promoting, adapting, importing, validating, or publishing\nanything. Provenance answers what source material is being used, what happened\nto it, and where the current object should be audited if it drifts.",
  "authority_scope_ref": "scope.lineage",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
