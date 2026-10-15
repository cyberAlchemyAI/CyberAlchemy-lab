<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Semantic Epoch

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.semantic-epoch`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-semantic-versioning`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Semantic Epoch is one immutable owner-selected version of an artifact's normative meaning. A successor Semantic Epoch is required exactly when the owner determines that the artifact's identity-preserving normative meaning, scope, exclusions, owned model, or semantic contracts materially changed. Representation-only revisions and derived refreshes do not create Semantic Epochs.

```text
NewSemanticEpoch(a_before,a_after) iff MaterialNormativeMeaning(a_before) != MaterialNormativeMeaning(a_after). RepresentationChanged and MeaningEqual does not imply NewSemanticEpoch.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| a_before | The selected predecessor semantic artifact. |
| a_after | The proposed postchange semantic artifact. |

### Boundary conditions

- A byte change alone does not prove semantic change.
- A claim that meaning is preserved is reviewable evidence, not automatic equivalence.
- A semantic successor requires explicit owner selection and applicable lineage.

### Testable conditions

- The change assessment separates semantic fields from representation fields.
- Every new epoch identifies its predecessor and material meaning delta.
- No representation-only change is classified as semantic lineage.

## Plain-language voice

A new chapter of meaning. It is created because what the artifact means changed, not merely because its JSON shape or generated documentation changed.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

A Governance context needs a new Semantic Epoch when its owned model or scope changes. Removing a redundant Context Map backreference while preserving that meaning should not produce a context v3 epoch.

### Examples

- Changing a Bounded Context's owned domain model is a semantic-epoch candidate.
- Re-encoding the same context under Bounded Context/v2 is not, by itself, a semantic epoch.

## Applicability

Versioned semantic artifacts whose normative meaning may change independently of representation.

### Exclusions

- Schema-only or encoding-only changes preserving meaning.
- Generated projection refreshes.
- Lifecycle labels inferred from filesystem paths.

## Boundaries

- Semantic Epoch is not Representation Revision.
- Semantic Epoch is not a generator version or schema revision.
- Filesystem version labels cannot establish semantic succession by themselves.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.bounded-context@2.0.0-candidate.1 | whole-json | `6ee155d2e7427e33357e55e56bc5228c2b584ea435bb9dc516ddb66385f590c0` | `admitted` |

## Primary consumers

- authority/definitions
- contexts/lineage
- tooling/validators

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.semantic-epoch`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.semantic-epoch@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |

## Evidence

- CTX08-drift-audit
- CAL-DECISION-0026-CTX06-REFERENCE-NORMALIZATION-DEFINITION-PROMOTION

## Residue

- definition-owner-admission-required
- semantic-change-assessment-contract-not-yet-authored

## Claim ceiling

This candidate defines semantic versioning meaning only. It does not classify any existing artifact, create lineage, or select a successor.
