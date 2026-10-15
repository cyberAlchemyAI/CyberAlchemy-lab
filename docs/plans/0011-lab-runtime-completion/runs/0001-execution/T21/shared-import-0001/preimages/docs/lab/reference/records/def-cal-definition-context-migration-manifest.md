[Documentation home](../../README.md)

# Context Migration Manifest

<a id="def-cal-definition-context-migration-manifest"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Context Migration Manifest

A reviewable plan identifying context material to move, destinations, changes, stopping conditions and how to reverse the move.

**When it applies**

Immutable planning candidates for one exact context migration epoch.

**Record formats**

[Context migration manifest · v2](type-cal-artifact-type-context-migration-manifest-v2.md#type-cal-artifact-type-context-migration-manifest-v2)

**A stated exclusion**

Source admission, execution authorization, file-copy commands, and migration receipts.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

The exact reviewable plan for what context material might move, where it would go, what would change, and how to stop or reverse safely.

## Exact governing statement

A Context Migration Manifest is an immutable candidate plan that binds exact source repository selectors and digests to explicit artifact dispositions, proposed destination identities and paths, dependency order, preimages, expected postimages, validation obligations, owner gates, rollback boundaries, exclusions, and unresolved residue for one bounded migration scope.

````
ContextMigrationManifest = (id, source_repository, source_selections, dispositions, destination_candidates, dependency_order, preimages, expected_postimages, validation_obligations, owner_gates, rollback_boundary, exclusions, residue, lifecycle); ManifestExists does not imply SourceAdmitted or MigrationAuthorized or Migrated.
````

- Every source is selector- and digest-bound.
- Every destination has explicit identity and path.
- Rollback and exclusions are declared before execution.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Definition and initial context promotion

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/context-migration-manifest/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.context-migration-manifest@1.0.0-candidate.1

**Content fingerprint · SHA-256**

bcfadcf568fe77a4e410e96ca86ba76f34bf8fdefdff2dfeb8cd12ac67022beb

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:cyberalchemy-lab-context-migration",
  "applicability": "Immutable planning candidates for one exact context migration epoch.",
  "exclusions": [
    "Source admission, execution authorization, file-copy commands, and migration receipts."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
