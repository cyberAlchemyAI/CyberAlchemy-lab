<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Capability Instance successor fixture

- Identity: `fixture.capability-instance.example`
- Schema version: `cyberalchemy-lab-capability-instance/v2`

## Canonical fixture

```json
{
  "adoption_decision_ref": "fixture:decision:adoption",
  "authority_effect": "none",
  "bounded_context_refs": [
    "fixture.context.example/v1"
  ],
  "capability_instance_id": "fixture.capability-instance.example",
  "capability_version_ref": "fixture.product-capability.example/v1",
  "claim_ceiling": "Fixture only; it does not instantiate, adopt, bind, or conform a Product Capability.",
  "classification": {
    "artifact_type_ref": "cal.artifact-type.capability-instance/v1",
    "authority_kind": "none",
    "lifecycle_posture_ref": "candidate:cal.lifecycle.artifact/v1:candidate-authored",
    "semantic_kind": "capability-instance"
  },
  "conformance_refs": [],
  "construction_binding_ref": "fixture:construction-binding",
  "coordination_context_ref": "fixture.coordination.example/v1",
  "drift_route": "fixture:route:instance-drift",
  "evidence_refs": [
    "fixture:evidence:instance"
  ],
  "extension_scope": {
    "exclusions": [
      "No parent mutation."
    ],
    "statement": "Fixture-only local specialization."
  },
  "inherited_contract_ref": "fixture:contract:inherited",
  "instance_authority_claim_ref": "fixture:authority-claim:instance",
  "owner_ref": "fixture:role:capability-instance-owner",
  "parent_authority_claim_ref": "fixture:authority-claim:parent",
  "recomposition_route": "fixture:route:recomposition",
  "recursion_stop": {
    "budget": 1,
    "condition": "Stop after one fixture level.",
    "kind": "budget"
  },
  "residue_refs": [
    "fixture:residue:parent-capability-unadmitted"
  ],
  "schema_version": "cyberalchemy-lab-capability-instance/v2",
  "source_direction": {
    "canonical": "instance.json",
    "generator_ref": "cal.generator.ctx01.capability-instance/v1",
    "generator_sha256": "0051171cb74670aa6ecf4ef488d4c128bdd34b5b4dffdc49d7430886e7449615",
    "human_projection": "INSTANCE.md",
    "projection_policy": "generated-only"
  },
  "status": "candidate-unadmitted",
  "terminal_handoff_ref": "fixture:handoff:terminal",
  "version": "1.0.0-fixture"
}
```

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, migration, deletion, or runtime effect.
