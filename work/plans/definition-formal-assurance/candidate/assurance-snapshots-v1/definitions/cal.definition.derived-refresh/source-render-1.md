<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Derived Refresh

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.derived-refresh`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-generated-projections`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Derived Refresh is the deterministic regeneration and validation of a noncanonical projection from an unchanged canonical machine input under an exact generator binding. It records the canonical input digest, generator identity and digest, output digest, parity result, and validation receipt. A Derived Refresh creates no Semantic Epoch, Representation Revision, Governance Decision, or authority effect. A change to the generator is governed separately as a tooling change even when refreshing its outputs has no semantic effect.

```text
DerivedRefresh(x,g,y) iff CanonicalInputDigest(x) unchanged and y = DeterministicGenerate(g,x) and Projection(y) and AuthorityEffect(y)=none. DerivedRefresh does not imply SemanticEpoch or RepresentationRevision.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | The unchanged canonical machine input. |
| g | The exact generator binding. |
| y | The regenerated noncanonical projection. |

### Boundary conditions

- If canonical machine bytes change, the operation is not a Derived Refresh.
- Generated output cannot redefine canonical meaning.
- A generator change follows its own tooling workflow and does not silently gain adoption.

### Testable conditions

- The canonical input digest is unchanged.
- Two renders with the same generator and input are byte-identical.
- The output declares generated-only posture and authority_effect none.

## Plain-language voice

Rebuilding a human or lookup view from unchanged canonical data. It should be checked, but it does not ask the semantic owner to approve the same meaning again.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

DEFINITION.md, CONTEXT.md, indexes, and reverse Context Map membership views are generated surfaces. Rebuilding them from unchanged canonical JSON is a Derived Refresh.

### Examples

- Regenerate DEFINITIONS-INDEX.md from an unchanged registry.
- Regenerate CONTEXT.md from an unchanged context.json without creating a context epoch.

## Applicability

Deterministic regeneration of noncanonical projections from unchanged canonical machine state.

### Exclusions

- Changes to canonical machine records.
- Semantic or representation revisions.
- Generator changes treated as implicitly adopted tooling authority.

## Boundaries

- Derived Refresh is not Representation Revision because canonical machine bytes remain unchanged.
- Projection validation is evidence, not approval.
- A changed generator may require a separate tooling decision but does not turn its outputs into semantic authority.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.bounded-context@2.0.0-candidate.1 | whole-json | `6ee155d2e7427e33357e55e56bc5228c2b584ea435bb9dc516ddb66385f590c0` | `admitted` |

## Primary consumers

- authority/definitions
- contexts
- tooling/generators
- tooling/validators

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.derived-refresh`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.derived-refresh@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |

## Evidence

- user-direction:machine-canonical-human-generated
- CAL-DECISION-0026-CTX06-REFERENCE-NORMALIZATION-DEFINITION-PROMOTION

## Residue

- definition-owner-admission-required
- derived-refresh-receipt-contract-not-yet-authored

## Claim ceiling

This candidate defines derived refresh semantics only. It does not regenerate any current projection, adopt a generator, or authorize tooling changes.
