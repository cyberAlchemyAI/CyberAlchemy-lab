<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Intent Fixture

- Identity: `intent:complete-cyberalchemy-v2-migration`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Attributed To**: `person-reference:repository-owner`
### Constraints

```json
[
  "Preserve exact source provenance from CyberAlchemy v2",
  "Require owner review before admitting each Artifact Type",
  "Do not activate consumers as a side effect of admission",
  "Keep Definitions, Artifact Types, instances, and runtime activation as separate decisions",
  "Do not silently discard unresolved migration residue"
]
```

### Current Output Hypothesis

```json
{
  "artifact_type_ref": "cal.artifact-type.artifact-type/v2",
  "description": "A reviewed and admitted set of Artifact Types for the reconstructed CyberAlchemy v2 concepts."
}
```

- **Direction**: `Preserve useful CyberAlchemy v2 concepts and operating decisions as governed CyberAlchemy Lab artifacts.`
- **Intent State**: `active`
- **Kind**: `intent`
- **Motivation**: `Reconstructed migration knowledge needs reviewed Artifact Types before repository tools and people can use it consistently.`
- **Owner Ref**: `role:artifact-type-owner`
- **Review Route**: `authority/artifact-types/candidates/0004-remaining-26-materialization/CATALOG.md`
### Revision History

```json
[]
```

- **Revision Route**: `route:artifact-type-owner-review`
### Satisfaction Refs

```json
[]
```

- **Scope Ref**: `scope:cyberalchemy-v2-to-lab-migration`
### Successor Refs

```json
[]
```

- **Target Pressure**: `Migration knowledge exists, but its Artifact Types are not yet available as admitted Lab authority.`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
