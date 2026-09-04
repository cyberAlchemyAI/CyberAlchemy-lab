<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Representation Revision

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.representation-revision`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-semantic-versioning`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Representation Revision is a new immutable machine-canonical encoding of an existing Semantic Epoch whose normative meaning and semantic identity are preserved while its schema binding, artifact-type representation contract, canonical field layout, or encoding changes. It binds exact predecessor and postimage digests, a representation revision identity, the preserved Semantic Epoch, the representation delta, equivalence evidence, validation, owner selection, and rollback. It does not create semantic-successor lineage.

```text
RepresentationRevision(r,a0,a1) iff SemanticIdentity(a0)=SemanticIdentity(a1) and SemanticEpoch(a0)=SemanticEpoch(a1) and NormativeMeaning(a0)=NormativeMeaning(a1) and CanonicalBytes(a0)!=CanonicalBytes(a1) and ExactPrePost(r,a0,a1).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| r | One immutable Representation Revision record. |
| a0 | The exact canonical predecessor representation. |
| a1 | The exact candidate postimage representation. |

### Boundary conditions

- Meaning preservation requires explicit evidence and owner selection.
- The predecessor remains immutable historical evidence.
- A representation revision cannot be used when semantic meaning changed.
- Context lineage is not created for representation-only change.

### Testable conditions

- Preimage and postimage digests are exact and distinct.
- Semantic identity and Semantic Epoch references are unchanged.
- The representation delta and rollback are explicit.
- No semantic-successor lineage is emitted.

## Plain-language voice

The same meaning written in a new canonical machine form. The old bytes stay as history, the new bytes are reviewed, but the artifact does not pretend to become a new semantic version.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

The CTX08 normalization should re-encode the admitted Governance and Ontology Lifecycle v2 contexts under Bounded Context/v2 without inventing semantic v3 contexts.

### Examples

- Remove canonical context_map_refs while retaining the same context identity, scope, owner, language, and domain model.
- Bind the v1 and v2 representation digests in a migration receipt while keeping the v2 Semantic Epoch.

## Applicability

Immutable machine-canonical postimages that preserve an artifact's semantic identity and Semantic Epoch while changing representation.

### Exclusions

- Changes to normative meaning, scope, exclusions, or owned model.
- In-place mutation of decision-bound bytes.
- Generated human projections whose canonical input is unchanged.

## Boundaries

- Representation Revision is not Semantic Epoch.
- Representation Revision is not Derived Refresh because canonical machine bytes change.
- Meaning equivalence is not inferred from matching labels or context IDs.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.bounded-context@2.0.0-candidate.1 | whole-json | `6ee155d2e7427e33357e55e56bc5228c2b584ea435bb9dc516ddb66385f590c0` | `admitted` |

## Primary consumers

- contexts/migrations
- contexts/governance
- contexts/ontology-lifecycle
- tooling/validators

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.representation-revision`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.representation-revision@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |

## Evidence

- CTX08-drift-audit
- CAL-DECISION-0027-CTX07-NORMALIZED-CONTEXT-ARTIFACT-TYPE-PROMOTION

## Residue

- definition-owner-admission-required
- representation-revision-artifact-type-not-yet-authored
- CTX08-replacement-not-authorized

## Claim ceiling

This candidate defines representation-versioning semantics only. It does not reclassify, replace, mutate, or admit any CTX08 artifact.
