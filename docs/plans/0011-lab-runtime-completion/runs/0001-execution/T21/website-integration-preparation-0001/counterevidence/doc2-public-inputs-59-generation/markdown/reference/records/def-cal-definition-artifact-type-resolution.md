[Documentation home](../../README.md)

# Artifact Type Resolution

<a id="def-cal-definition-artifact-type-resolution"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Artifact Type Resolution

# Artifact Type Resolution

Identifies a particular accepted record-type contract using an exact reference or declared identifying field. It reports unresolved or ambiguous results rather than guessing from filenames.

**When it applies**

Resolving a canonical machine carrier to exactly one admitted Artifact Type through explicit classification or a registry-declared discriminator.

**Record formats**

[Artifact type registry · v2](type-cal-artifact-type-artifact-type-registry-v2.md#type-cal-artifact-type-artifact-type-registry-v2) · [Artifact type request · v1](type-cal-artifact-type-artifact-type-request-v1.md#type-cal-artifact-type-artifact-type-request-v1)

**A stated exclusion**

Directory or filename inference.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-artifact-type-resolution-section-2"></a>

## Source explanatory wording

One reusable operation reads the file and registry, reports one exact contract or a clear unresolved/ambiguous result, and never guesses from the path.

<a id="def-cal-definition-artifact-type-resolution-section-3"></a>

## Exact governing statement

Artifact Type Resolution is an executable deterministic operation resolve_R(a) over one canonical machine carrier and one exact registry. An explicit exact reference may select an admitted-current or admitted-historical type; discriminator-only evidence selects admitted-current types. The operation returns resolved for exactly one match, unresolved for zero, and ambiguous for multiple distinct matches. Paths, filenames, extensions, and nearest-name similarity are excluded evidence.

````
M_R(a)=explicit_matches_admitted_R(a) union discriminator_matches_current_R(a); resolve_R(a)={resolved(t,state_R(t)) if |M|=1, unresolved if |M|=0, ambiguous(M) if |M|>1}; authority_effect(resolve_R)=none.
````

- An explicit candidate type reference does not become admitted by resolution.
- A schema_version may be a discriminator only when registered for exactly one type.
- Successful resolution is not schema validation or admission.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/6320c77c9ef2-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.artifact-type-resolution@1.0.0-candidate.2

**Content fingerprint · SHA-256**

6320c77c9ef26129857008ed429969a3c43d3a2c9a7edb21c22900d5d47a9303

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Resolving a canonical machine carrier to exactly one admitted Artifact Type through explicit classification or a registry-declared discriminator.",
  "authority_scope_ref": "scope:artifact-type-resolution",
  "exclusions": [
    "Directory or filename inference.",
    "Nearest-name matching.",
    "Treating an unadmitted candidate type as usable."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
