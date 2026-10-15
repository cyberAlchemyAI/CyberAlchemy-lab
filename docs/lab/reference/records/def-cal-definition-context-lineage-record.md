[Documentation home](../../README.md)

# Context Lineage Record

<a id="def-cal-definition-context-lineage-record"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Context Lineage Record

# Context Lineage Record

Records how an earlier context identity relates to its successors and which meanings were preserved or changed.

**When it applies**

Immutable identity-history statements relating exact predecessor and successor contexts.

**Record formats**

[Context lineage record · v2](type-cal-artifact-type-context-lineage-record-v2.md#type-cal-artifact-type-context-lineage-record-v2)

**A stated exclusion**

Migration planning, aliases, redirects, equivalence proofs, and deletion permission.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-context-lineage-record-section-2"></a>

## Source explanatory wording

The durable record explaining how an old context identity relates to its successors and which meanings stayed the same or changed.

<a id="def-cal-definition-context-lineage-record-section-3"></a>

## Exact governing statement

A Context Lineage Record is an immutable, owner-qualified statement relating exact predecessor and successor context identities through one typed lineage disposition, with source and destination versions, preserved and changed semantic scopes, decision evidence, effective boundary, challenges, and residue. It records identity history without inferring semantic equivalence or admission.

````
ContextLineageRecord = (id, predecessor_context_ref?, successor_context_refs, lineage_kind, source_version, destination_versions, preserved_scope, changed_scope, decision_ref, evidence_refs, effective_boundary, challenge_route, residue); lineage_kind in {preserved, successor, split, merged, superseded, withdrawn}; Lineage does not imply Equivalence or Admission.
````

- Predecessor and successor versions are exact.
- Preserved and changed scopes are independently stated.
- Directory continuity cannot imply semantic identity continuity.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Definition and initial context promotion

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/context-lineage-record/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.context-lineage-record@1.0.0-candidate.1

**Content fingerprint · SHA-256**

0e843dc8932020004432bf49f0f765f89e44c9e1f52e08b92037340a49c4b2d6

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:cyberalchemy-lab-context-migration",
  "applicability": "Immutable identity-history statements relating exact predecessor and successor contexts.",
  "exclusions": [
    "Migration planning, aliases, redirects, equivalence proofs, and deletion permission."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
