<!-- GENERATED FILE: edit system-ontology.json or its declared upstream source and run p2-build.py. -->

# System Ontology Prototype

> Generated human projection. The machine JSON remains canonical within this prototype epoch.

- System Ontology Id: `CAL-P2-SYSTEM-ONTOLOGY-DEFINITION-SNAPSHOT-CONSTRUCTION`
- Stage Id: `CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE`
- Authority Effect: `none`

## Machine projection

```json
{
  "artifact_type": "system-ontology-prototype",
  "authority_effect": "none",
  "canonicality": "generated-prototype",
  "claim_ceiling": "Generated P2 system obligations only; validation proves only the selected smoke behavior and grants no conformance or operational authority.",
  "generated_from": {
    "path": "compiled/graph.json",
    "sha256": "d4621ca7849d2c39056fb8c62a1ee4f7c555affd2532dde60d6af66b89534b83"
  },
  "implementation_contract": {
    "crate": "craft-p2-definition-snapshot",
    "expected_authority_effect": "none",
    "expected_legacy_id": "DS-D1.1",
    "expected_result_kind": "definition_snapshot_witness",
    "expected_term": "Entity",
    "language": "Rust"
  },
  "obligations": [
    {
      "obligation_id": "CAL-P2-OBLIGATION-STABLE-ID",
      "required_behavior": "Output preserves DS-D1.1 without renumbering.",
      "trace_ref": "CAL-P2-NODE-DEFINITION-WITNESS"
    },
    {
      "obligation_id": "CAL-P2-OBLIGATION-EXACT-SOURCE",
      "required_behavior": "Execution binds the selected DS-D1.1 source digest.",
      "trace_ref": "CAL-P2-NODE-SOURCE-DS-D1-1"
    },
    {
      "obligation_id": "CAL-P2-OBLIGATION-ENTITY-CRITERION",
      "required_behavior": "Output identifies Entity and its identity plus typedness criterion.",
      "trace_ref": "CAL-P2-NODE-DEFINITION-WITNESS"
    },
    {
      "obligation_id": "CAL-P2-OBLIGATION-NO-AUTHORITY",
      "required_behavior": "Output reports authority_effect none.",
      "trace_ref": "CAL-P2-NODE-CAPABILITY"
    }
  ],
  "prototype_epoch": "epoch-001",
  "schema_version": "cyberalchemy-lab-system-ontology-prototype/v1",
  "source_direction": {
    "canonical_upstream": "compiled/graph.json",
    "generator": "p2-build.py",
    "human_projection": "SYSTEM-ONTOLOGY.md"
  },
  "stage_id": "CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE",
  "system_ontology_id": "CAL-P2-SYSTEM-ONTOLOGY-DEFINITION-SNAPSHOT-CONSTRUCTION"
}
```

## Claim ceiling

Generated P2 system obligations only; validation proves only the selected smoke behavior and grants no conformance or operational authority.
