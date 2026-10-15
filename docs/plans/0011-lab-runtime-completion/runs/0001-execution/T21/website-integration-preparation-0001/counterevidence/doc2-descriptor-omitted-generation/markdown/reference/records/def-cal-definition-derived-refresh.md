[Documentation home](../../README.md)

# Derived Refresh

<a id="def-cal-definition-derived-refresh"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Derived Refresh

# Derived Refresh

Regenerates and validates a view from unchanged designated machine input under an exact generator binding. It creates no meaning revision, representation revision, decision or authority effect; generator changes are governed separately.

**When it applies**

Deterministic regeneration of noncanonical projections from unchanged canonical machine state.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Changes to canonical machine records.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-derived-refresh-section-2"></a>

## Source explanatory wording

Rebuilding a human or lookup view from unchanged canonical data. It should be checked, but it does not ask the semantic owner to approve the same meaning again.

<a id="def-cal-definition-derived-refresh-section-3"></a>

## Exact governing statement

A Derived Refresh is the deterministic regeneration and validation of a noncanonical projection from an unchanged canonical machine input under an exact generator binding. It records the canonical input digest, generator identity and digest, output digest, parity result, and validation receipt. A Derived Refresh creates no Semantic Epoch, Representation Revision, Governance Decision, or authority effect. A change to the generator is governed separately as a tooling change even when refreshing its outputs has no semantic effect.

````
DerivedRefresh(x,g,y) iff CanonicalInputDigest(x) unchanged and y = DeterministicGenerate(g,x) and Projection(y) and AuthorityEffect(y)=none. DerivedRefresh does not imply SemanticEpoch or RepresentationRevision.
````

- If canonical machine bytes change, the operation is not a Derived Refresh.
- Generated output cannot redefine canonical meaning.
- A generator change follows its own tooling workflow and does not silently gain adoption.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Craft foundation admission

**Original definition**

[Read the original record](../../assets/f017c0403a46-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.derived-refresh@1.0.0-candidate.1

**Content fingerprint · SHA-256**

f017c0403a46551ec8abfef4de24507a0ed42cc1b38acd54ec242683b89af171

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:cyberalchemy-lab-generated-projections",
  "applicability": "Deterministic regeneration of noncanonical projections from unchanged canonical machine state.",
  "exclusions": [
    "Changes to canonical machine records.",
    "Semantic or representation revisions.",
    "Generator changes treated as implicitly adopted tooling authority."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
