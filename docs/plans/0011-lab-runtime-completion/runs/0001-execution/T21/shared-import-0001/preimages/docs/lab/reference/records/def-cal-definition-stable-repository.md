[Documentation home](../../README.md)

# Stable Repository

<a id="def-cal-definition-stable-repository"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Stable Repository

A repository meeting declared criteria for a trustworthy, understandable and usable base. A release still needs evidence and the appropriate owner decision.

**When it applies**

Use this term when deciding whether CyberAlchemy v2 is ready to move from a project folder inside `domainspec-core` into its own repository. The repository is not stable merely because files exist; it is stable when its authority model, source spine, promotion gates, and validation surfaces are navigable and reviewable. When CyberAlchemy v2 is extracted, the stable repository objective is that a user can download CyberAlchemy as this governed base and build project or domain towers above it.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A stable repository is the trustworthy base someone can download, understand, and build on without guessing what counts.

## Exact governing statement

Stable Repository is the normalized definition identified by semantic.stable-repository, owned within scope.repository-governance, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D1 without silently merging it with another target.

Bound source-semantic basis:

A stable repository is a maintainable repository surface whose authority, source evidence, promoted contracts, validation evidence, implementation work, and operating traces can be understood without hidden conversation context, and whose exported base can support downstream construction without requiring users to rediscover or re-promote its foundation.

````
semantic.stable-repository := (semantic_kind=definition, carrier=type.definition, owner_scope=scope.repository-governance, source_set={CAV2-D1}). Identity, carrier, and owner scope are independent axes; equality of labels does not establish equality of concepts.
````

- This term does not mean finished product, public repository, automatic ownership of every historical CyberAlchemy source, or implementation complete. Standalone extraction and any transfer of authority from older source spaces remain promotion decisions.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/stable-repository/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.stable-repository@1.0.0-candidate.1

**Content fingerprint · SHA-256**

b5ff4c0de9c053902f13b9554d23cffddef4b8091cd69e05d2c7bce427935e6c

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use this term when deciding whether CyberAlchemy v2 is ready to move from a\nproject folder inside `domainspec-core` into its own repository. The repository\nis not stable merely because files exist; it is stable when its authority model,\nsource spine, promotion gates, and validation surfaces are navigable and\nreviewable. When CyberAlchemy v2 is extracted, the stable repository objective\nis that a user can download CyberAlchemy as this governed base and build project\nor domain towers above it.",
  "authority_scope_ref": "scope.repository-governance",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
