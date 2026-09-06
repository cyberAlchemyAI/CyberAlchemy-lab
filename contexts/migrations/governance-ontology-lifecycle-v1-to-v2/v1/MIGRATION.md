<!-- GENERATED FILE: edit migration.json and rerun generator.py. -->

# Context Migration Manifest: cal.context-migration.governance-ontology-lifecycle-v1-to-v2

> Generated from `migration.json`; this view is not canonical.

- Identity: `cal.context-migration.governance-ontology-lifecycle-v1-to-v2`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.context-migration-manifest/v1`
- Semantic kind: `context-migration-manifest`
- Authority effect: `none`

## Source Repository Ref

repository:CyberAlchemy-lab

## Source Selections

```json
[
  {
    "selector": "whole-file:contexts/governance/v1/context.json",
    "sha256": "e4d8ffb21383276b7f5a0d84d097d02507dcc2711d7197f285308430da28c9a4",
    "source_ref": "cal.context.governance/v1"
  },
  {
    "selector": "whole-file:contexts/governance/v1/language.json",
    "sha256": "7b6e2a22aa6c0ae1762178e22fe8c56c6c1cbe6bab4951012ba51757d3a220a5",
    "source_ref": "cal.language.governance/v1"
  },
  {
    "selector": "whole-file:contexts/ontology-lifecycle/v1/context.json",
    "sha256": "dc06e7e0b986262192f3578983368ad9c7c407d3a223e424f44c60717a6e7b0c",
    "source_ref": "cal.context.ontology-lifecycle/v1"
  },
  {
    "selector": "whole-file:contexts/ontology-lifecycle/v1/language.json",
    "sha256": "0e1b71f658bcf0dfdcc75b7a086d41bbae525413780a675330b05316b13d3b86",
    "source_ref": "cal.language.ontology-lifecycle/v1"
  },
  {
    "selector": "whole-file:contexts/maps/governance-ontology-lifecycle/v1/map.json",
    "sha256": "e4c339df5f2072a2a43b34ca2fe1f11ea331f53fc5a0616249d37150e2a242fd",
    "source_ref": "cal.context-map.governance-ontology-lifecycle/v1"
  }
]
```

## Dispositions

```json
[
  {
    "destination_ref": "cal.context.governance/v2",
    "disposition": "revise",
    "source_ref": "cal.context.governance/v1"
  },
  {
    "destination_ref": "cal.language.governance/v2",
    "disposition": "revise",
    "source_ref": "cal.language.governance/v1"
  },
  {
    "destination_ref": "cal.context.ontology-lifecycle/v2",
    "disposition": "revise",
    "source_ref": "cal.context.ontology-lifecycle/v1"
  },
  {
    "destination_ref": "cal.language.ontology-lifecycle/v2",
    "disposition": "revise",
    "source_ref": "cal.language.ontology-lifecycle/v1"
  },
  {
    "destination_ref": "cal.context-map.governance-ontology-lifecycle/v1",
    "disposition": "preserve",
    "source_ref": "cal.context-map.governance-ontology-lifecycle/v1"
  }
]
```

## Destination Candidates

```json
[
  {
    "artifact_id": "cal.context.governance/v2",
    "artifact_type_ref": "cal.artifact-type.bounded-context/v1",
    "path": "contexts/governance/v2/context.json"
  },
  {
    "artifact_id": "cal.language.governance/v2",
    "artifact_type_ref": "cal.artifact-type.ubiquitous-language/v1",
    "path": "contexts/governance/v2/language.json"
  },
  {
    "artifact_id": "cal.context.ontology-lifecycle/v2",
    "artifact_type_ref": "cal.artifact-type.bounded-context/v1",
    "path": "contexts/ontology-lifecycle/v2/context.json"
  },
  {
    "artifact_id": "cal.language.ontology-lifecycle/v2",
    "artifact_type_ref": "cal.artifact-type.ubiquitous-language/v1",
    "path": "contexts/ontology-lifecycle/v2/language.json"
  },
  {
    "artifact_id": "cal.context-lineage.governance.v1-to-v2",
    "artifact_type_ref": "cal.artifact-type.context-lineage-record/v1",
    "path": "contexts/lineage/governance/v1/lineage.json"
  },
  {
    "artifact_id": "cal.context-lineage.ontology-lifecycle.v1-to-v2",
    "artifact_type_ref": "cal.artifact-type.context-lineage-record/v1",
    "path": "contexts/lineage/ontology-lifecycle/v1/lineage.json"
  }
]
```

## Dependency Order

- CAL-DECISION-0024-GOVERNANCE-ONTOLOGY-LIFECYCLE-CONTEXT-MAP-PROMOTION
- cal.context.governance/v2
- cal.language.governance/v2
- cal.context.ontology-lifecycle/v2
- cal.language.ontology-lifecycle/v2
- cal.context-lineage.governance.v1-to-v2
- cal.context-lineage.ontology-lifecycle.v1-to-v2
- CAL-CONTEXT-PACK-CTX05-0001:validation
- role-separated-owner-review
- separate-migration-execution-decision

## Preimages

```json
[
  {
    "path": "contexts/governance/v1/context.json",
    "sha256": "e4d8ffb21383276b7f5a0d84d097d02507dcc2711d7197f285308430da28c9a4"
  },
  {
    "path": "contexts/governance/v1/language.json",
    "sha256": "7b6e2a22aa6c0ae1762178e22fe8c56c6c1cbe6bab4951012ba51757d3a220a5"
  },
  {
    "path": "contexts/ontology-lifecycle/v1/context.json",
    "sha256": "dc06e7e0b986262192f3578983368ad9c7c407d3a223e424f44c60717a6e7b0c"
  },
  {
    "path": "contexts/ontology-lifecycle/v1/language.json",
    "sha256": "0e1b71f658bcf0dfdcc75b7a086d41bbae525413780a675330b05316b13d3b86"
  },
  {
    "path": "contexts/maps/governance-ontology-lifecycle/v1/map.json",
    "sha256": "e4c339df5f2072a2a43b34ca2fe1f11ea331f53fc5a0616249d37150e2a242fd"
  }
]
```

## Expected Postimages

```json
[
  {
    "expected_condition": "Candidate exists with sha256=5c59ae8dc12807ad8996749a82e1f9b0c1f624b3ef87aaebf4442e957d90d88f and context_map_refs exactly [cal.context-map.governance-ontology-lifecycle/v1].",
    "path": "contexts/governance/v2/context.json"
  },
  {
    "expected_condition": "Candidate exists with sha256=ba84484be3f0d793e935ba4bbf960885ce1adcd2d2763aee940396ff290918d7 and reciprocally references cal.context.governance/v2.",
    "path": "contexts/governance/v2/language.json"
  },
  {
    "expected_condition": "Candidate exists with sha256=4a8ef8f3441a055aeed10e368db4bcec7bf6c098e15e2356cfd25d659df3a4b8 and context_map_refs exactly [cal.context-map.governance-ontology-lifecycle/v1].",
    "path": "contexts/ontology-lifecycle/v2/context.json"
  },
  {
    "expected_condition": "Candidate exists with sha256=8d01b878d93fa1b502d57348b8c5cad3c25968504de0ef7df37b17e63dda2e55 and reciprocally references cal.context.ontology-lifecycle/v2.",
    "path": "contexts/ontology-lifecycle/v2/language.json"
  },
  {
    "expected_condition": "Candidate exists with sha256=6e09af319953649599c081ea029c3827b639e7282a224eeeeeb795032dc56c98 and denies inferred equivalence and admission.",
    "path": "contexts/lineage/governance/v1/lineage.json"
  },
  {
    "expected_condition": "Candidate exists with sha256=95298b5e68d963d9a2e4f2cb55d5b825defe96783310dcbea6832bf8a12d48bc and denies inferred equivalence and admission.",
    "path": "contexts/lineage/ontology-lifecycle/v1/lineage.json"
  }
]
```

## Validation Obligations

- All seven canonical candidates validate against their admitted CTX01 artifact schemas.
- Every v2 context-language pair is reciprocal and pins the same 1.1.0-candidate.1 epoch.
- Both v2 contexts reference exactly the admitted Context Map and no reverse edge is introduced.
- Every v1 source selection has exactly one disposition and its current bytes match the declared preimage digest.
- Every destination condition binds current candidate bytes and deterministic generated projections.
- Lineage records name exact predecessors and successors and keep equivalence_inferred and admission_inferred false.
- Migration execution remains false and all predecessor bytes remain unchanged.

## Owner Gates

```json
[
  {
    "effect": "Separate exact admission decision for cal.context.governance/v2 only.",
    "role_ref": "role:governance-context-owner"
  },
  {
    "effect": "Separate exact admission decision for cal.language.governance/v2 only.",
    "role_ref": "role:governance-language-owner"
  },
  {
    "effect": "Separate exact admission decision for cal.context.ontology-lifecycle/v2 only.",
    "role_ref": "role:ontology-lifecycle-context-owner"
  },
  {
    "effect": "Separate exact admission decision for cal.language.ontology-lifecycle/v2 only.",
    "role_ref": "role:ontology-lifecycle-language-owner"
  },
  {
    "effect": "Separate exact admission of each lineage record without inferring equivalence, supersession, or migration completion.",
    "role_ref": "role:context-lineage-owner"
  },
  {
    "effect": "Confirm whether a successor map epoch must replace the admitted v1 endpoint references before any cutover.",
    "role_ref": "role:context-map-owner"
  },
  {
    "effect": "Separate immutable execution decision after all predecessor, destination, validation, rollback, and owner-admission gates are current.",
    "role_ref": "role:context-migration-owner"
  }
]
```

## Rollback Boundary

Authorship is additive and performs no cutover. The admitted v1 contexts, v1 languages, and v1 Context Map must remain byte-identical and undeleted. If a later separately authorized cutover fails, restore every consumer to the admitted v1 context-language references and v1 map, verify all five declared preimage digests, preserve failed successor bytes and receipts as evidence, and require a new owner decision before retry. Deletion, history rewriting, or source-package relocation is outside this manifest.

## Exclusions

- No v2 context, language, lineage record, or migration manifest is admitted by authorship or validation.
- No source-domain package under cyberAlchemy-v2/ontology/governance or ontology-lifecycle is selected, copied, moved, renamed, rewritten, or admitted.
- No successor Context Map epoch, reverse relationship, global relationship-kind artifact, payload schema, or Anti-Corruption Layer adapter is authored or inferred.
- No capability instance, DomainSpec source, system ontology, runtime, implementation binding, or conformance claim is migrated.
- No cutover, deletion, destructive action, commit, push, publication, deployment, external effect, or stable release is authorized.

## Owner Ref

role:context-migration-owner

## Immutable

`true`

## Execution Authority

`false`

## Evidence

- CAL-CONTEXT-PACK-CTX05-0001
- CAL-DECISION-0023-GOVERNANCE-AND-ONTOLOGY-LIFECYCLE-CONTEXT-PROMOTION
- CAL-DECISION-0024-GOVERNANCE-ONTOLOGY-LIFECYCLE-CONTEXT-MAP-PROMOTION
- cal.context-lineage.governance.v1-to-v2
- cal.context-lineage.ontology-lifecycle.v1-to-v2

## Residue

- residue:successor-context-language-and-lineage-owner-admissions-required
- residue:successor-map-epoch-decision-required-before-cutover
- residue:migration-execution-decision-not-authored
- residue:physical-source-package-relocation-requires-separate-source-admission-and-migration-manifest

## Claim ceiling

This immutable candidate plans only the additive v1-to-v2 context metadata transition for two context-language pairs while preserving the admitted v1 Context Map and all predecessor bytes. It does not admit any candidate, select physical source-package relocation, authorize migration execution or deletion, commit, publish, deploy, or establish a stable release.
