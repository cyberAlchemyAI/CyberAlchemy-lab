<!-- GENERATED FILE: canonical data is record.json. -->

# Governance history for Artifact Type Definition node

- Identity: `governance-event-history:node-artifact-type-definition`
- Kind: `governance-event-history`
- Record state: `candidate`
- Authority effect: `none`

## Payload

```json
{
  "append_only": true,
  "chain_digest": "1111111111111111111111111111111111111111111111111111111111111111",
  "event_records_are_replay_source": true,
  "events": [
    {
      "event_digest": "3333333333333333333333333333333333333333333333333333333333333333",
      "event_id": "governance-event:node-artifact-type-definition:842",
      "governance_cursor": 1,
      "previous_event_digest": null,
      "record_ref": "event-record:governance:1",
      "semantic_event_ref": {
        "semantic_cursor": 842,
        "semantic_event_digest": "2222222222222222222222222222222222222222222222222222222222222222",
        "semantic_event_id": "semantic-event:node-artifact-type-definition:842"
      },
      "upstream_governance_evidence_refs": [
        "decision:artifact-type-admission"
      ]
    }
  ],
  "history_id": "governance-event-history:node-artifact-type-definition",
  "history_manifest_is_event_index": true,
  "latest_governance_cursor": 1,
  "ontology_ref": "ontology:artifact-governance",
  "semantic_patch_forbidden": true,
  "stream_id": "governance:ontology-node:artifact-type-definition",
  "subject_ref": "ontology-node:artifact-type-definition"
}
```

## Claim ceiling

Candidate Step 7 example only; no admission, authority, relation, migration, or runtime effect.
