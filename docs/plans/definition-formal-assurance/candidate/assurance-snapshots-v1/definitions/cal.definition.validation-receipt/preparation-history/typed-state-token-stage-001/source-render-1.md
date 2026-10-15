<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Validation Receipt

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.validation-receipt`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:validation-receipt-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Validation Receipt is an immutable record R of one validation event. R binds exact identities and digests for the subject, criteria profile, validator, inputs, environment, complete outcomes, evidence, causal blockers, and claim ceiling. Recording R preserves traceability but cannot change the subject's authority or lifecycle by itself.

```text
R = (receipt_id, subject@digest, profile@digest, validator@digest, inputs@digests, environment, outcomes, evidence_refs, blockers, emitted_at, claim_ceiling, authority_effect=none); exists(R) =/=> conforms(subject) or admitted(subject).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| R | One immutable Validation Receipt. |

### Boundary conditions

- The receipt is bound to exact evaluated bytes and profile.
- Every declared check outcome and causal blocker is preserved.
- The receipt authority effect is none.

### Testable conditions

- Changing an evaluated input changes or invalidates the receipt binding.
- A receipt cannot omit declared dependent checks.
- Consumers cannot infer conformance or admission merely from receipt existence or PASS.

## Plain-language voice

A Validation Receipt is the detailed record of what was checked, against what, with which tool, and what happened. It is a receipt, not an approval stamp.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

CML-07 receipts preserve the exact candidate, schema, source, projection, and fixture results used at the final decision boundary while keeping the decision itself separate.

### Examples

- The semantic-closure receipt lists every Definition digest and hostile fixture outcome.
- The Artifact Type/v2 receipt proves schema and projection checks but does not admit v2.

## Applicability

The immutable evidence record emitted for one Validation, binding its exact subject, profile, validator, inputs, environment, outcomes, residue, and claim ceiling.

### Exclusions

- The Validation procedure itself.
- A Conformance assertion unless separately assessed.
- An admission, acceptance, authority, publication, or deployment decision.

## Boundaries

- Validation Receipt is not Validation procedure.
- Validation Receipt is not Conformance assessment.
- Validation Receipt is not Decision or Authority.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.evaluation.definition/v1 | whole-json | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| domainspec-core:CAV2-D38 | lines:2509-2571 | `8472c2f6b75902c8ce2a81ae1b3980657662d2b519571a948e43580f79889fb5` | `candidate-unadmitted` |

## Primary consumers

- authority/definitions/candidates/0007-cml07-semantic-closure/receipts/validation.json
- authority/artifact-types/artifact-type/v2/receipts/validation.json
- docs/identity-packs/0002-craft-identity-chain-semantic-closure/receipts/validation.json

## Lookup and drift

- Index: `authority/definitions/candidates/0007-cml07-semantic-closure/DEFINITIONS-INDEX.md` / `cal.definition.validation-receipt@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0007-cml07-semantic-closure/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- SC-001

## Residue

- A dedicated admitted Validation Receipt Artifact Type remains future work.

## Claim ceiling

This candidate defines Validation Receipt semantics only. It does not admit any receipt format or elevate a recorded PASS into conformance or authority.
