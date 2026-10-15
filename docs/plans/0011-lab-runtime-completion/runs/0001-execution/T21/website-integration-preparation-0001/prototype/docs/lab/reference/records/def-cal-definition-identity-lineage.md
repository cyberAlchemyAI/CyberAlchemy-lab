[Documentation home](../../README.md)

# Identity Lineage

<a id="def-cal-definition-identity-lineage"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Identity Lineage

# Identity Lineage

Records continuity and change across a rename or successor, with explicit ownership. Similar names or contents are insufficient to establish the same identity.

**When it applies**

An immutable, typed, evidence-backed continuity relation among exact identity epochs that states whether a change preserves identity, creates a successor identity, or records another declared lineage kind.

**Record formats**

[Identity lineage · v1](type-cal-artifact-type-identity-lineage-v1.md#type-cal-artifact-type-identity-lineage-v1)

**A stated exclusion**

A generic alias list.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-identity-lineage-section-2"></a>

## Source explanatory wording

Identity Lineage records what stayed the same and what changed across a rename or successor. Similar names or files are not enough; the continuity must be explicit and owned.

<a id="def-cal-definition-identity-lineage-section-3"></a>

## Exact governing statement

Identity Lineage is a typed relation L over exact identity epochs. L binds a subject kind, predecessor and successor identities or epochs, lineage kind, owner decision, evidence, and non-effects. A same-identity rename preserves one identity across named epochs; it does not create a new Product, Project, Method, Goal, or Context. Lineage types are subject-kind specific unless an explicitly generalized contract is admitted.

````
L = (lineage_id, subject_kind_definition_ref, predecessor_ref, successor_ref, lineage_kind, owner_decision_ref, evidence_refs, non_effects); same_identity_rename(a,b) => identity(a)=identity(b) and name(a)!=name(b); similar(a,b) =/=> same_identity(a,b).
````

- The subject kind and lineage kind are explicit.
- The owner decision and evidence supporting continuity are bound.
- A context-specific lineage contract cannot govern Product lineage by analogy.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Semantic foundation admission

**Original definition**

[Read the original record](../../assets/32c15860fb06-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.identity-lineage@1.0.0-candidate.1

**Content fingerprint · SHA-256**

32c15860fb0621edaf172efea9f1f5ab467763a5ca4454d0d2424e7783c499bf

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:identity-lineage-definition",
  "applicability": "An immutable, typed, evidence-backed continuity relation among exact identity epochs that states whether a change preserves identity, creates a successor identity, or records another declared lineage kind.",
  "exclusions": [
    "A generic alias list.",
    "Context Lineage Record used outside Context semantics.",
    "Identity equality inferred from similar names, paths, owners, content, or history."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
