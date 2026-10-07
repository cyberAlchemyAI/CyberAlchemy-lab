<!-- GENERATED FILE: canonical data is record.json. -->

# Artifact governance ontology manifest

- Identity: `ontology-manifest:artifact-governance`
- Kind: `ontology-manifest`
- Record state: `candidate`
- Authority effect: `none`

## Payload

```json
{
  "branch_policy": "business-system-bridge-explicit",
  "challenge_contract_ref": "challenge-contract:artifact-governance",
  "configuration_digest": "3333333333333333333333333333333333333333333333333333333333333333",
  "governance_history_ref": "governance-event-history:artifact-governance",
  "ontology_definition_ref": "cal.definition.ontology@1.0.0-candidate.1",
  "ontology_owner_ref": "role:ontology-owner",
  "ontology_ref": "ontology:artifact-governance",
  "ontology_version": "1.0.0-candidate.1",
  "policy_refs": [
    "policy:admitted-authority-first"
  ],
  "projection_contract_refs": [
    "projection-contract:ontology-view/v1"
  ],
  "relation_kind_registry_ref": "relation-kind-registry:lab-global/v1",
  "runtime_binding_ref": "cal.binding.ontology-product-event-runtime/v2",
  "semantic_history_ref": "semantic-event-history:artifact-governance",
  "state_model_ref": "ontology-state-model:event-sourced/v1",
  "subject_replay_source": false
}
```

## Claim ceiling

Candidate Step 7 example only; no admission, authority, relation, migration, or runtime effect.
