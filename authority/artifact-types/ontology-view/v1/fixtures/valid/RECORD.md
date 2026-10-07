<!-- GENERATED FILE: canonical data is record.json. -->

# Artifact review ontology view

- Identity: `ontology-view:artifact-review:842`
- Kind: `ontology-view`
- Record state: `candidate`
- Authority effect: `none`

## Payload

```json
{
  "consumer_ref": "agent-session:artifact-review:001",
  "cut_digest": "3333333333333333333333333333333333333333333333333333333333333333",
  "cut_ref": "ontology-cut:artifact-governance:842",
  "exclusions": [
    "runtime activation",
    "implicit authority"
  ],
  "expires_at": "2026-10-07T12:00:00Z",
  "freshness_at": "2026-10-06T12:00:00Z",
  "governance_join_policy_ref": "governance-join:exact-event-tuple/v1",
  "intended_use": "Review exact Artifact Type and Definition bindings.",
  "ontology_ref": "ontology:artifact-governance",
  "replay_source": false,
  "selected_edge_refs": [
    "ontology-edge:definition-carries-meaning"
  ],
  "selected_node_refs": [
    "ontology-node:artifact-type-definition"
  ],
  "selector_ref": "ontology-selector:artifact-review",
  "semantic_cursor": 842,
  "source_event_set_digest": "1111111111111111111111111111111111111111111111111111111111111111"
}
```

## Claim ceiling

Candidate Step 7 example only; no admission, authority, relation, migration, or runtime effect.
