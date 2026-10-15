[Documentation home](../../README.md)

# Artifact Surface Classification

<a id="def-cal-definition-artifact-surface-classification"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Artifact Surface Classification

# Artifact Surface Classification

Requires every governed file to have exactly one declared role, including the package manifest itself. A folder location cannot silently determine that role.

**When it applies**

Classifying every governed file by its explicit role in one canonical package without inferring meaning from its path or extension.

**Record formats**

[Canonical package manifest · v1](type-cal-artifact-type-canonical-package-manifest-v1.md#type-cal-artifact-type-canonical-package-manifest-v1)

**A stated exclusion**

Treating every file as an independent artifact instance.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-artifact-surface-classification-section-2"></a>

## Source explanatory wording

Every important file needs one declared job, and the manifest must list itself too. Its location never decides its role.

<a id="def-cal-definition-artifact-surface-classification-section-3"></a>

## Exact governing statement

Every governed file f in package P, including P's package.json manifest, has exactly one declared surface role from canonical-instance, declared-component, generated-projection, evidence, fixture, or transient-state. The manifest self-entry is a canonical instance of Canonical Package Manifest/v1. Every canonical instance resolves to exactly one admitted Artifact Type; every other role cannot silently become canonical.

````
for all f in governed(P), exists exactly one role_P(f) in {I,C,G,E,F,T}; role_P(package.json)=I and type(package.json)=CanonicalPackageManifest/v1; role_P(f)=I => |resolve_R(f)|=1; role_P(f)!=I => not canonical_subject(f).
````

- A directory is not a surface role.
- A schema or validator may be a declared component without being an independent artifact instance.
- Transient state cannot satisfy canonical dependencies.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/552b583d5bc7-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.artifact-surface-classification@1.0.0-candidate.2

**Content fingerprint · SHA-256**

552b583d5bc7efb4567fde4483064fbd63275963e4b79cf0da3cc6c16f3cdc83

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Classifying every governed file by its explicit role in one canonical package without inferring meaning from its path or extension.",
  "authority_scope_ref": "scope:artifact-surface-classification",
  "exclusions": [
    "Treating every file as an independent artifact instance.",
    "Inferring authority or identity from directory placement.",
    "Allowing an unexplained governed file to affect validation or execution."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
