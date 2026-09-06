<!-- GENERATED FILE: edit product-capability.json or its declared upstream source and run p2-build.py. -->

# Definition Snapshot Construction Product Capability Prototype

> Generated human projection. The machine JSON remains canonical within this prototype epoch.

- Capability Id: `CAL-PROTOTYPE-CAPABILITY-DEFINITION-SNAPSHOT-CONSTRUCTION`
- Stage Id: `CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE`
- Status: `prototype`
- Authority Effect: `none`

## Machine projection

```json
{
  "artifact_type": "product-capability-prototype",
  "authority_effect": "none",
  "canonicality": "non-authoritative",
  "capability_id": "CAL-PROTOTYPE-CAPABILITY-DEFINITION-SNAPSHOT-CONSTRUCTION",
  "challenge_route": "role:craft-project-owner",
  "claim_ceiling": "This is a provisional Product Capability identity for one P2 learning vertical. It is not the System Construction Product Feature, an adopted Product Capability, a capability instance, a Bounded Context, an admission, an approval, or operational authority.",
  "consumers": [
    "P2 prototype compiler",
    "P2 Rust implementation",
    "P2 independent validator"
  ],
  "context_posture": {
    "final_placement": "deferred-until-tested-candidate",
    "kind": "explicit-no-context",
    "reason": "This P2 product prototype is not owned by the Governance or Ontology Lifecycle languages, and directory placement cannot create a DDD Bounded Context."
  },
  "contracts": [
    "selected source bytes must match exact selectors and digests",
    "generated graph and system ontology must reproduce from the authored specification",
    "Rust behavior must check the exact system-ontology obligations",
    "all prototype records must retain authority_effect none"
  ],
  "evidence_route": "product/prototypes/craft-first-capability/epoch-001/evidence/smoke-test.json",
  "name": "Definition Snapshot Construction",
  "outcome": "Enable an owner to transform one exact, source-selected legacy meta-type into a deterministic Craft definition-snapshot witness whose business meaning, authored specification, compiled graph, system obligations, and Rust behavior remain traceable by digest.",
  "p1_binding": {
    "receipt_path": "product/prototypes/craft-first-capability/epoch-001/ontology/receipts/validation.json",
    "receipt_sha256": "32d4a1ea31cd7cfea7be587019a0a37e256e48ecfe005c1503b0293f52bcc62e",
    "required_stage_state": "TESTED_PROTOTYPE",
    "scaffold_id": "CAL-CML08-P1-CRAFT-AGENT-ONTOLOGY-SCAFFOLD-EPOCH-001",
    "scaffold_path": "product/prototypes/craft-first-capability/epoch-001/ontology/scaffold.json",
    "scaffold_sha256": "cc9991441507e329d838ca00c28301d26f268dc132250be76594f189b51ebc3b"
  },
  "participants": [
    "role:craft-project-owner",
    "role:prototype-definition-contributor",
    "role:prototype-implementation-builder"
  ],
  "product_binding": {
    "path": "product/products/craft/v1/product.json",
    "posture": "candidate-product-context-only",
    "product_id": "CA2-PRODUCT-CRAFT",
    "repository": "/home/vrondelli/projects/CyberAlchemy-lab",
    "sha256": "f5282222e1fb3b50ec671aac04d29673192deb5c39089c04d472f4e22f95a3a4"
  },
  "product_feature_relation": {
    "feature_id": "CA2-PRODUCT-FEATURE-SYSTEM-CONSTRUCTION",
    "identity_rule": "Product Capability and Product Feature remain distinct identities",
    "path": "cyberAlchemy-v2/goals/projects/craft/product-feature/product-feature.json",
    "relation_posture": "prototype-hint",
    "relation_type": "contributes_to",
    "repository": "/home/vrondelli/projects/domainspec-core",
    "sha256": "3f19206bdbc2fd462c1d058fa0786eb28aa7b8676f0831289c1afb96aaab0077"
  },
  "prototype_epoch": "epoch-001",
  "schema_version": "cyberalchemy-lab-product-capability-prototype/v1",
  "scope": {
    "excludes": [
      "the other twelve active backend meta-types",
      "Lean evidence",
      "Definition admission",
      "Product Capability adoption",
      "broad consumer migration",
      "runtime activation"
    ],
    "includes": [
      "one DS-D1.1 Entity source witness",
      "one deterministic Craft snapshot witness",
      "one compiled graph and system-ontology chain",
      "one offline Rust smoke result"
    ]
  },
  "source_direction": {
    "canonical": "product-capability.json",
    "generator": "../p2-build.py",
    "human_projection": "PRODUCT-CAPABILITY.md",
    "projection_policy": "generated-only"
  },
  "stage_id": "CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE",
  "status": "prototype"
}
```

## Claim ceiling

This is a provisional Product Capability identity for one P2 learning vertical. It is not the System Construction Product Feature, an adopted Product Capability, a capability instance, a Bounded Context, an admission, an approval, or operational authority.
