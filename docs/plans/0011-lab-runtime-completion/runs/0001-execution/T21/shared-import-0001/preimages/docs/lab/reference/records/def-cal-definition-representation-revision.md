[Documentation home](../../README.md)

# Representation Revision

<a id="def-cal-definition-representation-revision"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Representation Revision

A new designated machine encoding or representation contract that preserves the artifact’s accepted meaning. Earlier contents remain recorded rather than being silently overwritten.

**When it applies**

Immutable machine-canonical postimages that preserve an artifact's semantic identity and Semantic Epoch while changing representation.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Changes to normative meaning, scope, exclusions, or owned model.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

The same meaning written in a new canonical machine form. The old bytes stay as history, the new bytes are reviewed, but the artifact does not pretend to become a new semantic version.

## Exact governing statement

A Representation Revision is a new immutable machine-canonical encoding of an existing Semantic Epoch whose normative meaning and semantic identity are preserved while its schema binding, artifact-type representation contract, canonical field layout, or encoding changes. It binds exact predecessor and postimage digests, a representation revision identity, the preserved Semantic Epoch, the representation delta, equivalence evidence, validation, owner selection, and rollback. It does not create semantic-successor lineage.

````
RepresentationRevision(r,a0,a1) iff SemanticIdentity(a0)=SemanticIdentity(a1) and SemanticEpoch(a0)=SemanticEpoch(a1) and NormativeMeaning(a0)=NormativeMeaning(a1) and CanonicalBytes(a0)!=CanonicalBytes(a1) and ExactPrePost(r,a0,a1).
````

- Meaning preservation requires explicit evidence and owner selection.
- The predecessor remains immutable historical evidence.
- A representation revision cannot be used when semantic meaning changed.
- Context lineage is not created for representation-only change.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Craft foundation admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0003-single-decision-checkpoint/definitions/representation-revision/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.representation-revision@1.0.0-candidate.1

**Content fingerprint · SHA-256**

5bb818e70b0281dc14edcd4dade418335f50df93bc30c607823ecce5b3349850

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:cyberalchemy-lab-semantic-versioning",
  "applicability": "Immutable machine-canonical postimages that preserve an artifact's semantic identity and Semantic Epoch while changing representation.",
  "exclusions": [
    "Changes to normative meaning, scope, exclusions, or owned model.",
    "In-place mutation of decision-bound bytes.",
    "Generated human projections whose canonical input is unchanged."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
