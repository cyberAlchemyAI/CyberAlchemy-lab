<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Context Lineage Record

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.context-lineage-record`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-context-migration`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Context Lineage Record is an immutable, owner-qualified statement relating exact predecessor and successor context identities through one typed lineage disposition, with source and destination versions, preserved and changed semantic scopes, decision evidence, effective boundary, challenges, and residue. It records identity history without inferring semantic equivalence or admission.

```text
ContextLineageRecord = (id, predecessor_context_ref?, successor_context_refs, lineage_kind, source_version, destination_versions, preserved_scope, changed_scope, decision_ref, evidence_refs, effective_boundary, challenge_route, residue); lineage_kind in {preserved, successor, split, merged, superseded, withdrawn}; Lineage does not imply Equivalence or Admission.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| lineage_kind | One explicit relation from the closed lineage disposition set. |

### Boundary conditions

- Predecessor and successor versions are exact.
- Preserved and changed scopes are independently stated.
- Directory continuity cannot imply semantic identity continuity.

### Testable conditions

- The lineage kind belongs to the closed set.
- Decision evidence and challenge route are present.
- No equivalence or admission is inferred from lineage alone.

## Plain-language voice

The durable record explaining how an old context identity relates to its successors and which meanings stayed the same or changed.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

Ontology Lifecycle will need lineage from the current unclassified vertical to any future bounded-context package; filesystem continuity alone will not prove semantic continuity.

### Examples

- A split can preserve one predecessor while producing separately owned Governance and Ontology Lifecycle successor identities.

## Applicability

Immutable identity-history statements relating exact predecessor and successor contexts.

### Exclusions

- Migration planning, aliases, redirects, equivalence proofs, and deletion permission.

## Boundaries

- A Context Lineage Record is not a migration manifest, source admission, Context Map, alias, redirect, Git rename, equivalence proof, promotion decision, or permission to delete the predecessor.
- A lineage record preserves withdrawal and supersession history rather than erasing it.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| CAL-SOURCE-ADMISSION-CTX00-CAV2-D29 | CAV2-D29 | `f47b8ae8dcbfcc97d624871a5aab03cbf3ffdea2b341046a0bba1edbb59740be` | `admitted` |
| CAL-SOURCE-ADMISSION-CTX00-CAV2-D66 | CAV2-D66 | `93ed5c852579f7e84af9c3163f737f4f37c822d1a49063a3fa8b5af1d2ae7769` | `admitted` |

## Primary consumers

- authority/lineage
- contexts
- docs/migrations

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.context-lineage-record`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.context-lineage-record@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |

## Evidence

- CAL-DECISION-0016-ONTOLOGY-LIFECYCLE-CONTEXT-PLACEMENT
- CAL-DECISION-0017-CTX00-SOURCE-ADMISSION

## Residue

- context-lineage-artifact-type-required
- lineage-owner-binding-required
- predecessor-and-successor-context-identities-required

## Claim ceiling

This candidate defines Context Lineage Record meaning only; it neither states a real lineage relation nor authorizes moving or deleting predecessor bytes.
