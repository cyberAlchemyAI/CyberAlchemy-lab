<!-- GENERATED FILE: edit business-ontology.json or its declared upstream source and run p2-build.py. -->

# Definition Snapshot Construction Business Ontology Prototype

> Generated human projection. The machine JSON remains canonical within this prototype epoch.

- Ontology Id: `CAL-PROTOTYPE-ONTOLOGY-DEFINITION-SNAPSHOT-CONSTRUCTION`
- Stage Id: `CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE`
- Status: `prototype`
- Authority Effect: `none`

## Machine projection

```json
{
  "artifact_type": "capability-local-business-ontology-prototype",
  "authority_effect": "none",
  "canonicality": "non-authoritative",
  "capability_binding": {
    "capability_id": "CAL-PROTOTYPE-CAPABILITY-DEFINITION-SNAPSHOT-CONSTRUCTION",
    "path": "product/product-capability.json",
    "sha256": "fc43224a3573241d126fc1d98a69c6311704f9f8b0c19cf7180f1200221085dd"
  },
  "claim_ceiling": "This capability-local business ontology is a bounded P2 prototype. It is not a canonical ontology, a Bounded Context language, an admitted definition snapshot, or a runtime authority.",
  "closure": {
    "ambient_imports": "forbidden",
    "deferred_legacy_ids": [
      "DS-D1.2",
      "DS-D1.3",
      "DS-D1.4",
      "DS-D1.5",
      "DS-D1.6",
      "DS-D1.7",
      "DS-D1.8",
      "DS-D1.9",
      "DS-D1.11",
      "DS-D1.12",
      "DS-D1.13",
      "DS-D1.14"
    ],
    "reserved_tombstones": [
      "DS-D1.10"
    ],
    "selected_legacy_ids": [
      "DS-D1.1"
    ]
  },
  "concepts": [
    {
      "concept_id": "CAL-P2-CONCEPT-SOURCE-BINDING",
      "kind": "value-object-prototype",
      "required_fields": [
        "repository",
        "path",
        "selector",
        "sha256"
      ]
    },
    {
      "concept_id": "CAL-P2-CONCEPT-DEFINITION-WITNESS",
      "identity_field": "legacy_id",
      "kind": "entity-prototype",
      "required_fields": [
        "legacy_id",
        "term",
        "category",
        "criterion_ref",
        "source_bindings"
      ]
    },
    {
      "concept_id": "CAL-P2-CONCEPT-CONSTRUCTION-TRACE",
      "kind": "value-object-prototype",
      "required_fields": [
        "predecessor_ref",
        "predecessor_sha256",
        "output_ref",
        "output_sha256"
      ]
    }
  ],
  "context_posture": "explicit-no-context",
  "ontology_id": "CAL-PROTOTYPE-ONTOLOGY-DEFINITION-SNAPSHOT-CONSTRUCTION",
  "prototype_epoch": "epoch-001",
  "relation_types": [
    {
      "posture": "prototype-relation",
      "relation_type": "selects",
      "source_kind": "Product Capability Prototype",
      "target_kind": "Source Binding"
    },
    {
      "posture": "prototype-relation",
      "relation_type": "materializes_as",
      "source_kind": "Legacy Meta-Type Witness",
      "target_kind": "Craft Definition Snapshot Witness"
    },
    {
      "posture": "prototype-relation",
      "relation_type": "traces_to",
      "source_kind": "Craft Definition Snapshot Witness",
      "target_kind": "Construction Trace"
    }
  ],
  "rules": [
    {
      "rule_id": "CAL-P2-RULE-EXACT-SOURCE",
      "statement": "A source is usable only when its exact selected bytes reproduce the bound digest."
    },
    {
      "rule_id": "CAL-P2-RULE-STABLE-ID",
      "statement": "The DS-D1.1 identity is preserved as legacy lineage and cannot be silently replaced or renumbered."
    },
    {
      "rule_id": "CAL-P2-RULE-GENERATED-DIRECTION",
      "statement": "Graph, system ontology, Rust contract, and human projections are generated downstream of authored specification bytes."
    },
    {
      "rule_id": "CAL-P2-RULE-NO-AUTHORITY",
      "statement": "Successful prototype construction or smoke testing creates no semantic or operational authority."
    }
  ],
  "schema_version": "cyberalchemy-lab-business-ontology-prototype/v1",
  "source_direction": {
    "canonical": "business-ontology.json",
    "generator": "../p2-build.py",
    "human_projection": "BUSINESS-ONTOLOGY.md",
    "projection_policy": "generated-only"
  },
  "stage_id": "CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE",
  "status": "prototype",
  "ubiquitous_language": [
    {
      "meaning": "An explicit repository, path, selector, and digest tuple that bounds which legacy bytes the prototype may use.",
      "term": "Source Selection",
      "term_id": "CAL-P2-TERM-SOURCE-SELECTION"
    },
    {
      "meaning": "One selected active legacy meta-type used to prove the construction path without admitting or copying the complete legacy registry.",
      "term": "Legacy Meta-Type Witness",
      "term_id": "CAL-P2-TERM-LEGACY-META-TYPE-WITNESS"
    },
    {
      "meaning": "One machine-canonical prototype record preserving the selected semantic ID, meaning, criterion binding, and provenance.",
      "term": "Craft Definition Snapshot Witness",
      "term_id": "CAL-P2-TERM-SNAPSHOT-WITNESS"
    },
    {
      "meaning": "A digest-closed path from capability through business meaning, authored specification, graph, system obligations, implementation, and evidence.",
      "term": "Construction Trace",
      "term_id": "CAL-P2-TERM-CONSTRUCTION-TRACE"
    }
  ]
}
```

## Claim ceiling

This capability-local business ontology is a bounded P2 prototype. It is not a canonical ontology, a Bounded Context language, an admitted definition snapshot, or a runtime authority.
