<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Context View Fixture

- Identity: `context-view:remaining-18-review:2026-10-05`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Challenge Route**: `route:context-view-challenge`
- **Claim Ceiling**: `This immutable view records a bounded projection. It is not the Context itself and does not make included claims true.`
- **Context Ref**: `context:lab-artifact-type-admission`
- **Context Version Ref**: `context:lab-artifact-type-admission@sha256:79e1`
### Excluded Material

```json
[
  {
    "reason": "Outside the repository review Context",
    "source_ref": "runtime:live-services"
  }
]
```

- **Expires At**: `2026-10-06T15:05:00Z`
- **Generated At**: `2026-10-05T15:05:00Z`
### Included Material

```json
[
  {
    "selector": "admitted entries bound by remaining 18 packages",
    "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "source_ref": "authority/definitions/registry.json"
  }
]
```

- **Kind**: `context-view`
### Limitations

```json
[
  "The view covers repository state at one source epoch"
]
```

### Lineage Refs

```json
[
  "context-request:remaining-18-review",
  "receipt:remaining-18-model-validation"
]
```

- **Owner Ref**: `role:artifact-type-owner`
- **Owner Route**: `role:context-view-owner`
- **Request Ref**: `context-request:remaining-18-review`
- **Scope Ref**: `scope:cyberalchemy-lab-model-review`
- **Selection Basis**: `Exact request selectors and admitted-authority-first source policy.`
- **Source Epoch**: `git-worktree:2026-10-05T15:05:00Z`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
