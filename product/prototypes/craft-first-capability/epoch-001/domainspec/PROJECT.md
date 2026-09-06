<!-- GENERATED FILE: edit project.json or its declared upstream source and run p2-build.py. -->

# Craft Definition Snapshot Construction Specification Prototype

> Generated human projection. The machine JSON remains canonical within this prototype epoch.

- Specification Id: `CAL-P2-SPEC-DEFINITION-SNAPSHOT-CONSTRUCTION`
- Stage Id: `CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE`
- Status: `prototype`
- Authority Effect: `none`

## Machine projection

```json
{
  "artifact_type": "authored-craft-specification-prototype",
  "authority_effect": "none",
  "canonicality": "machine-canonical-within-prototype",
  "claim_ceiling": "This authored Craft specification is a P2 prototype source for one DS-D1.1 witness. It does not admit the witness as a Definition, select a final Product Capability or Bounded Context, migrate consumers, or authorize runtime activation.",
  "compile_contract": {
    "compiler_id": "CAL-P2-PYTHON-DETERMINISTIC-PROTOTYPE-COMPILER",
    "compiler_path": "p2-build.py",
    "generated_outputs": [
      "compiled/graph.json",
      "compiled/system-ontology.json",
      "implementation/src/generated_contract.rs"
    ],
    "graph_nodes": [
      "CAL-P2-NODE-CAPABILITY",
      "CAL-P2-NODE-BUSINESS-ONTOLOGY",
      "CAL-P2-NODE-SOURCE-DS-D1-1",
      "CAL-P2-NODE-DEFINITION-WITNESS"
    ],
    "graph_relations": [
      "requires_meaning_from",
      "selects_source",
      "materializes_as"
    ],
    "system_obligations": [
      "CAL-P2-OBLIGATION-STABLE-ID",
      "CAL-P2-OBLIGATION-EXACT-SOURCE",
      "CAL-P2-OBLIGATION-ENTITY-CRITERION",
      "CAL-P2-OBLIGATION-NO-AUTHORITY"
    ]
  },
  "context_posture": {
    "bounded_context_ref": null,
    "kind": "explicit-no-context",
    "placement_rule": "Prototype colocation supplies no Bounded Context identity or language authority."
  },
  "definition_snapshot_witness": {
    "category": "structural",
    "criterion": {
      "identity": "at-least-one truthy Identity field",
      "typedness": "all fields declare a non-empty Type"
    },
    "distinguisher": "An Entity has a designated identity field; a Value Object has none and declares equality by value.",
    "legacy_id": "DS-D1.1",
    "one_line": "identity-bearing, lifecycle-tracked object with at least one declared identity field",
    "source_binding_refs": [
      "CAL-P2-SOURCE-DS-D1-1-MACHINE-INDEX",
      "CAL-P2-SOURCE-DS-D1-1-HUMAN-CARD",
      "CAL-P2-SOURCE-DS-D1-1-CRITERION"
    ],
    "status": "active-at-selected-source",
    "term": "Entity"
  },
  "input_bindings": [
    {
      "path": "product/product-capability.json",
      "ref": "CAL-PROTOTYPE-CAPABILITY-DEFINITION-SNAPSHOT-CONSTRUCTION",
      "role": "product-capability-prototype",
      "sha256": "fc43224a3573241d126fc1d98a69c6311704f9f8b0c19cf7180f1200221085dd"
    },
    {
      "path": "business/business-ontology.json",
      "ref": "CAL-PROTOTYPE-ONTOLOGY-DEFINITION-SNAPSHOT-CONSTRUCTION",
      "role": "capability-local-business-ontology-prototype",
      "sha256": "cb8684c2889e7c168ad8641b4e3ebc162338caa21f746e389e6e0f810542df02"
    },
    {
      "path": "docs/construction-chains/0002-craft-first-product-candidate-v2/chain.json",
      "ref": "CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE",
      "role": "p2-stage-contract",
      "sha256": "6ce5972ca93b541ca6fce8b8160539812160685293ea5ac290239018a88dd149"
    }
  ],
  "lineage": {
    "admission_posture": "not-requested",
    "current_id": "DS-D1.1",
    "former_product_name": "DomainSpec v2",
    "identity_posture": "same-id-prototype-preservation",
    "legacy_id": "DS-D1.1",
    "renumbering": "forbidden"
  },
  "name": "Craft Definition Snapshot Construction Specification",
  "prototype_epoch": "epoch-001",
  "recomposition_route": {
    "route": "author a successor prototype epoch and regenerate every downstream digest",
    "trigger": "a selected source, prototype meaning, capability identity, or context posture changes"
  },
  "recursion_stop": {
    "condition": "Stop after DS-D1.1; do not traverse the remaining registry, criterion references, DS-D8 relations, fixtures, or implementation consumers.",
    "kind": "exact-selected-source-count",
    "value": 1
  },
  "rollback_boundary": {
    "consumer_effect": "none",
    "destructive_actions": "forbidden",
    "legacy_source_effect": "none",
    "scope": "product/prototypes/craft-first-capability/epoch-001 P2 additive files only"
  },
  "schema_version": "cyberalchemy-lab-authored-craft-specification-prototype/v1",
  "source_direction": {
    "canonical": "project.json",
    "generator": "../p2-build.py",
    "human_projection": "PROJECT.md",
    "projection_policy": "generated-only"
  },
  "source_selections": [
    {
      "classification": "reference-external-prototype-input",
      "path": "projects/domainspec-v2/definitions/meta-types/meta-types.yml",
      "repository": "/home/vrondelli/projects/domainspec-core",
      "selected_bytes_sha256": "6c63e20e31707fe0701ca018827931f4f4040a2e674942af020560d73c5e6d26",
      "selector": "yaml-member:id=DS-D1.1;end-before=DS-D1.2",
      "source_id": "CAL-P2-SOURCE-DS-D1-1-MACHINE-INDEX",
      "whole_file_sha256": "bc800afdca36fa701a13ec611e7ee0ef928a4c8d259d48dfac2880a3cc8cbbc4"
    },
    {
      "classification": "reference-external-prototype-input",
      "path": "projects/domainspec-v2/definitions/meta-types/meta-types.md",
      "repository": "/home/vrondelli/projects/domainspec-core",
      "selected_bytes_sha256": "8f79f9b02e8749cb89fd8decabcf7e79233dbd38015f3d376ab639a5b972ae89",
      "selector": "heading:## DS-D1.1 \u00b7 Entity (Structural);end-before=next-level-2-heading",
      "source_id": "CAL-P2-SOURCE-DS-D1-1-HUMAN-CARD",
      "whole_file_sha256": "c49f7879f7d27f214f930dc0c643edf411e63bf26d1a057f81be959645f51a51"
    },
    {
      "classification": "reference-external-prototype-input",
      "path": "projects/domainspec-v2/impl/spec/meta-types/structural/entity.schema.yml",
      "repository": "/home/vrondelli/projects/domainspec-core",
      "selected_bytes_sha256": "cfdd6cade80ba32cefa8716e008468b1848d9311d2e82555a9428464feb06dc7",
      "selector": "whole-file",
      "source_id": "CAL-P2-SOURCE-DS-D1-1-CRITERION",
      "whole_file_sha256": "cfdd6cade80ba32cefa8716e008468b1848d9311d2e82555a9428464feb06dc7"
    }
  ],
  "specification_id": "CAL-P2-SPEC-DEFINITION-SNAPSHOT-CONSTRUCTION",
  "stage_id": "CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE",
  "status": "prototype",
  "terminal_handoff": {
    "effect": "construction evidence only",
    "on_fail": "role:craft-project-owner",
    "on_pass": "CML10-P3-ITERATE-AND-TEST-PROTOTYPE-SPINE"
  }
}
```

## Claim ceiling

This authored Craft specification is a P2 prototype source for one DS-D1.1 witness. It does not admit the witness as a Definition, select a final Product Capability or Bounded Context, migrate consumers, or authorize runtime activation.
