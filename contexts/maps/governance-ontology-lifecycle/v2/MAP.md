<!-- GENERATED FILE: edit map.json and rerun generator.py. -->

# Context Map: cal.context-map.governance-ontology-lifecycle

> Generated from `map.json`; this view is not canonical.

- Identity: `cal.context-map.governance-ontology-lifecycle`
- Version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.context-map/v2`
- Semantic kind: `context-map`
- Authority effect: `none`

## Context Refs

- cal.context.governance/v2
- cal.context.ontology-lifecycle/v2

## Relationships

```json
[
  {
    "authority_boundary": "Governance remains the sole semantic and decision authority for its outcome. Ontology Lifecycle may record, order, replay, and project evidence of that outcome, but it cannot create, adopt, amend, revoke, reinterpret, invalidate, or enforce a Governance Decision. This relationship transfers immutable evidence and never transfers authority, ownership, admission, or permission.",
    "contract_refs": [
      "cal.context.governance/v2",
      "cal.language.governance/v2",
      "cal.context.ontology-lifecycle/v2",
      "cal.language.ontology-lifecycle/v2",
      "cal.definition.context-map@2.0.0-candidate.1"
    ],
    "direction": "source-to-target",
    "information_boundary": "Governance publishes only one immutable owner-decision evidence envelope containing exact decision identity and version, subject reference, source digest, authority scope, lifecycle or admission outcome, effective boundary, challenge route, and cited evidence references. Ontology Lifecycle translates that envelope into local Governance Event and Exact Semantic Event Reference records while preserving the upstream identity and digest. Missing, ambiguous, stale, or unmapped fields become Typed Residue; credentials, mutable Governance internals, implicit classifications, and enforcement capability do not cross.",
    "owner_refs": [
      "role:context-map-owner",
      "role:governance-context-owner",
      "role:governance-language-owner",
      "role:ontology-lifecycle-context-owner",
      "role:ontology-lifecycle-language-owner"
    ],
    "relationship_id": "cal.context-relationship.governance-to-ontology-lifecycle.authority-decision-feed",
    "relationship_kind_ref": "candidate:ddd.upstream-downstream.published-language.anticorruption-layer/v1",
    "source_context_ref": "cal.context.governance/v2",
    "target_context_ref": "cal.context.ontology-lifecycle/v2",
    "translation_refs": [
      "cav2.governance-model#node:GovernanceDecision",
      "ontology-lifecycle.governance-event",
      "ontology-lifecycle.exact-semantic-event-reference"
    ]
  }
]
```

## Owner Refs

- role:context-map-owner
- role:governance-context-owner
- role:governance-language-owner
- role:ontology-lifecycle-context-owner
- role:ontology-lifecycle-language-owner

## Drift Route

role:context-map-owner

## Evidence

- CAL-DECISION-0024-GOVERNANCE-ONTOLOGY-LIFECYCLE-CONTEXT-MAP-PROMOTION
- CAL-DECISION-0025-GOVERNANCE-ONTOLOGY-LIFECYCLE-SUCCESSOR-PROMOTION
- CAL-DECISION-0026-CTX06-REFERENCE-NORMALIZATION-DEFINITION-PROMOTION
- CAL-DECISION-0027-CTX07-NORMALIZED-CONTEXT-ARTIFACT-TYPE-PROMOTION
- CAL-D65S8ADM-0032

## Residue

- residue:context-map-v2-product-test-pending
- residue:context-map-v2-product-approval-pending
- residue:d65-epoch-002-not-yet-compiled
- residue:adapter-export-and-cutover-not-authorized

## Claim ceiling

This additive candidate binds the admitted Governance and Ontology Lifecycle v2 endpoint versions through one directional evidence-translation relationship. It does not admit or activate the map, create a reverse dependency, transfer authority, mutate the admitted v1 map or D65-S8 runtime, export an adapter, migrate, cut over, publish, release, deploy, or establish a stable release.
