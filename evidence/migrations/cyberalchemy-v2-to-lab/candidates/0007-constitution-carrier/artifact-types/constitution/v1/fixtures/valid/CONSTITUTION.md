<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Constitution Fixture

- Identity: `CAL-IMPORT-RULEBOOK-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.constitution/v1`
- **Authority Level**: `proposed-owner-scoped`
- **Challenge Route**: `role:definition-owner`
- **Claim Ceiling**: `Candidate demonstration. Matching a subject does not adopt this rulebook or activate its rules.`
- **Composition**: `all-matching-rules-no-implicit-override`
- **Conflict Route**: `role:repository-migration-owner`
- **Downstream Effect**: `preview-only`
- **Owner Route**: `role:repository-migration-owner`
### Policies

```json
[
  {
    "policy_id": "no-counts-only-completion",
    "rule_ids": [
      "preserve-counts",
      "preserve-meaning"
    ],
    "statement": "Matching counts alone cannot establish a complete semantic migration."
  }
]
```

### Precedence

```json
[
  "preserve-counts",
  "preserve-meaning"
]
```

### Retirement Or Split Conditions

```json
[
  "Split the rulebook if new consumers require different scopes or owners.",
  "Retire this version after an explicit successor decision for a different source corpus."
]
```

### Rules

```json
[
  {
    "grounding_refs": [
      "semantic.invariant"
    ],
    "rule_id": "preserve-counts",
    "selector_ids": [
      "selected-runtime"
    ],
    "statement": "The initial imported store must preserve the manifest's node, relation and supporting-document counts.",
    "validation_binding_id": "import-counts",
    "validation_mode": "deterministic"
  },
  {
    "grounding_refs": [
      "semantic.typed-coupling-invariant"
    ],
    "rule_id": "preserve-meaning",
    "selector_ids": [
      "selected-runtime"
    ],
    "statement": "Review source-qualified identities and explicit lineage residue before claiming semantic equivalence.",
    "validation_binding_id": null,
    "validation_mode": "review"
  }
]
```

- **Schema Version**: `cyberalchemy-lab-constitution/v1`
- **Scope Ref**: `scope:v4-sibling-import-genesis`
### Selectors

```json
[
  {
    "attribute": "runtime_ref",
    "equals": "runtime:v4-sibling-import",
    "selector_id": "selected-runtime"
  }
]
```

### Source Direction

```json
{
  "canonical": "constitution.json",
  "human_projection": "CONSTITUTION.md",
  "projection_policy": "generated-only"
}
```

### Subject Kinds

```json
[
  "artifact"
]
```

### Validation Bindings

```json
[
  {
    "binding_id": "import-counts",
    "evaluation_profile": "candidate:integer-observation-comparison/v1",
    "invariant_id": "CAL-IMPORT-COUNTS-001",
    "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0006-invariant-carrier/artifact-types/invariant/v1/fixtures/valid/invariant.json",
    "sha256": "47c7d107efa1ecee8ff8b2a13c9f81318bbfc970b94db4c9e5e14e9c869b491f"
  }
]
```

- **Version**: `1.0.0-candidate.1`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
