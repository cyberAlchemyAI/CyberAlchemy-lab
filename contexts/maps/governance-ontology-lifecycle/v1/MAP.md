<!-- GENERATED FILE: edit map.json and rerun generator.py. -->

# Context Map: cal.context-map.governance-ontology-lifecycle

> Generated from `map.json`; this view is not canonical.

- Identity: `cal.context-map.governance-ontology-lifecycle`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.context-map/v1`
- Semantic kind: `context-map`
- Authority effect: `none`

## Context Refs

- cal.context.governance/v1
- cal.context.ontology-lifecycle/v1

## Relationships

```json
[
  {
    "authority_boundary": "Governance remains the sole semantic and decision authority for the published outcome. Ontology Lifecycle may record, order, replay, and project evidence of that outcome but cannot create, adopt, amend, revoke, invalidate, reinterpret, or enforce a Governance Decision. The Published Language and downstream Anti-Corruption Layer transfer information, never authority, ownership, admission, or permission.",
    "contract_refs": [
      "cal.context.governance/v1",
      "cal.language.governance/v1",
      "cal.context.ontology-lifecycle/v1",
      "cal.language.ontology-lifecycle/v1",
      "cal.definition.context-map@1.0.0-candidate.1"
    ],
    "direction": "source-to-target",
    "information_boundary": "Governance publishes only an exact immutable owner-decision envelope: decision identity and version, decision kind, subject reference, source digest, authority scope, lifecycle or admission outcome, effective boundary, challenge route, and cited evidence references. Ontology Lifecycle may translate that envelope into its local Governance Event and Exact Semantic Event Reference records while preserving the exact upstream identity and digest. Missing, ambiguous, or unmapped fields become Typed Residue; mutable Governance internals, implicit classifications, credentials, and enforcement capability do not cross.",
    "owner_refs": [
      "role:context-map-owner",
      "role:governance-context-owner",
      "role:governance-language-owner",
      "role:ontology-lifecycle-context-owner",
      "role:ontology-lifecycle-language-owner"
    ],
    "relationship_id": "cal.context-relationship.governance-to-ontology-lifecycle.authority-decision-feed",
    "relationship_kind_ref": "candidate:ddd.upstream-downstream.published-language.anticorruption-layer/v1",
    "source_context_ref": "cal.context.governance/v1",
    "target_context_ref": "cal.context.ontology-lifecycle/v1",
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

- CAL-DECISION-0016-ONTOLOGY-LIFECYCLE-CONTEXT-PLACEMENT
- CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION
- CAL-DECISION-0022-CONTEXT-OPERATIONAL-OWNER-PROMOTION
- CAL-DECISION-0023-GOVERNANCE-AND-ONTOLOGY-LIFECYCLE-CONTEXT-PROMOTION
- CAL-CONTEXT-MAP-PACK-CTX04-0001

## Residue

- residue:context-map-owner-admission-required
- residue:relationship-kind-remains-map-local-candidate
- residue:runtime-payload-schema-and-adapter-not-authored
- residue:ontology-lifecycle-to-governance-reverse-feedback-not-authorized
- residue:endpoint-context-map-references-require-successor-context-epochs-after-map-admission

## Claim ceiling

This artifact proposes one directional Governance-to-Ontology-Lifecycle Context Map relationship using an upstream/downstream Published Language and downstream Anti-Corruption Layer pattern. It does not admit the map or relationship kind, create a reverse dependency, admit either source ontology, authorize a runtime adapter, migration, implementation, publication, deployment, or stable release.
