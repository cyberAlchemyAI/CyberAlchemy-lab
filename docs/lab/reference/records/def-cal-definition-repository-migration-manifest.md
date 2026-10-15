[Documentation home](../../README.md)

# Repository Migration Manifest

<a id="def-cal-definition-repository-migration-manifest"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Repository Migration Manifest

# Repository Migration Manifest

An exact moving plan identifying source items, destinations, content fingerprints, collision handling and rollback scope. It neither performs nor authorizes the move.

**When it applies**

An immutable, exact-byte, source-to-target repository migration envelope that binds complete source accounting, exclusions, unique mappings, a target baseline, a copy allowlist, an expected postimage, validation obligations, and rollback boundaries.

**Record formats**

[Artifact type · v1](type-cal-artifact-type-repository-migration-manifest-v1.md#type-cal-artifact-type-repository-migration-manifest-v1)

**A stated exclusion**

Context-local semantic succession, which remains owned by Context Migration Manifest.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-repository-migration-manifest-section-2"></a>

## Source explanatory wording

This is the sealed moving list for one repository migration: every source item is counted, every file to copy has one destination and digest, collisions stop the move, and the rollback list says exactly what the move could create. The list itself never performs or approves the move.

<a id="def-cal-definition-repository-migration-manifest-section-3"></a>

## Exact governing statement

A Repository Migration Manifest M binds source snapshot S, target baseline T0, total accounting partition A=(C,E), injective mapping f:C->P, expected postimage T1, validation set V, and rollback set R. M is well formed only when every observed source entry occurs exactly once in C or E, every selected regular file has one digest-bound destination, f has no divergent collision with T0, execution_authority=false, and R equals the set of paths that an authorized additive execution may create.

````
M=(S,T0,C,E,f,T1,V,R); C disjoint E; C union E=entries(S); injective(f); collision(f(C),T0)=empty; authorize(M)=false; R=create_set(M).
````

- Every source entry is accounted for without an ambient glob at execution time.
- Divergent existing target bytes block rather than overwrite.
- Imported bytes remain non-authoritative until separately classified and admitted.
- Runtime installations are reconstructed from canonical profiles and locks.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0011-repository-migration-manifest/definitions/repository-migration-manifest/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.repository-migration-manifest@1.0.0-candidate.1

**Content fingerprint · SHA-256**

253ea99d7c599e81354d1fcdc63bd27c216062c652ad66c67dbcd7d4369145c6

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An immutable, exact-byte, source-to-target repository migration envelope that binds complete source accounting, exclusions, unique mappings, a target baseline, a copy allowlist, an expected postimage, validation obligations, and rollback boundaries.",
  "authority_scope_ref": "scope:repository-migration-manifest-definition",
  "exclusions": [
    "Context-local semantic succession, which remains owned by Context Migration Manifest.",
    "Source admission, target activation, product approval, execution authorization, source deletion, overwrite, publication, release, or deployment.",
    "Installed dependencies, build products, caches, or host-specific runtime state reconstructed from profiles and locks."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
