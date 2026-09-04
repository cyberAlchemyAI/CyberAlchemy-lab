<!-- GENERATED FILE: canonical data is the sibling JSON fixture. -->

# Identity Graph Fixture

- Identity: `fixture:graph:craft`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical field projection

- **Schema Version**: `cyberalchemy-lab-identity-graph/v1`
- **Version**: `1.0.0-candidate.1`
- **Name**: `Craft identity graph`
### Semantic Definition Refs

```json
[
  "cal.definition.identity-relation@1.0.0-candidate.1",
  "cal.definition.identity-carrier@1.0.0-candidate.1",
  "cal.definition.product@1.0.0-candidate.1",
  "CAV2-D60@1.0.0-candidate.1",
  "CAV2-D32@1.0.0-candidate.1",
  "CAV2-D59@1.0.0-candidate.1"
]
```

### Nodes

```json
[
  {
    "identity_kind": "product",
    "identity_ref": "fixture:product:cyberalchemy"
  },
  {
    "identity_kind": "product",
    "identity_ref": "fixture:product:craft"
  },
  {
    "identity_kind": "project",
    "identity_ref": "fixture:project:craft-migration"
  },
  {
    "identity_kind": "method",
    "identity_ref": "CAV2-D20"
  },
  {
    "identity_kind": "goal",
    "identity_ref": "fixture:goal:craft-foundation"
  }
]
```

### Relations

```json
[
  {
    "relation_id": "fixture:relation:contains-craft",
    "relation_kind": "contains_product",
    "source_ref": "fixture:product:cyberalchemy",
    "target_ref": "fixture:product:craft"
  },
  {
    "relation_id": "fixture:relation:craft-coordinated",
    "relation_kind": "coordinated_by",
    "source_ref": "fixture:product:craft",
    "target_ref": "fixture:project:craft-migration"
  },
  {
    "relation_id": "fixture:relation:craft-embodies-method",
    "relation_kind": "embodies_method",
    "source_ref": "fixture:product:craft",
    "target_ref": "CAV2-D20"
  },
  {
    "relation_id": "fixture:relation:project-uses-method",
    "relation_kind": "uses_method",
    "source_ref": "fixture:project:craft-migration",
    "target_ref": "CAV2-D20"
  },
  {
    "relation_id": "fixture:relation:project-pursues-goal",
    "relation_kind": "pursues_goal",
    "source_ref": "fixture:project:craft-migration",
    "target_ref": "fixture:goal:craft-foundation"
  }
]
```

- **Graph Owner Ref**: `role:identity-graph-owner`
### Evidence Refs

```json
[
  "fixture:evidence:identity-graph"
]
```

- **Challenge Route**: `role:identity-graph-owner`
- **Claim Ceiling**: `Fixture only; graph validity does not admit endpoints, relations, or carriers.`

## Projection boundary

This document is generated from the canonical machine fixture and adds no identity, relation, lifecycle, conformance, or authority field.
