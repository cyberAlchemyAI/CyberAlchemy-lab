<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Validation

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.validation`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:validation-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

Validation is an Evaluation V of exact subject S against exact criteria profile P. V produces check outcomes and a receipt. A PASS establishes only that every evaluable criterion declared by P passed for the bound inputs; it becomes conformance evidence only when an applicable conformance profile declares those checks sufficient for an exact scope.

```text
validate(P@digest, S@digest, I@digest) -> receipt(O); PASS(V) =/=> conforms(S,C,Q); PASS(V) =/=> admitted(S).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| V | One validation evaluation. |
| P | The exact validation profile and criteria. |
| O | The complete set of validation outcomes. |

### Boundary conditions

- The validation profile declares its coverage and evaluation mode.
- A PASS cannot cover omitted or NOT_EVALUABLE checks.
- Conformance and authority decisions remain separately owned.

### Testable conditions

- Subject, profile, inputs, validator identity, and outcomes are recorded.
- All declared checks have PASS, FAIL, or NOT_EVALUABLE outcomes.
- No PASS is reported as admission or runtime conformance by implication.

## Plain-language voice

Validation runs known checks. A PASS means those checks passed for those exact inputs—not that every possible requirement is satisfied or that anything was approved.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

CML-07 validation checks schemas, references, projections, hostile fixtures, and dependency currency. Later conformance assessment decides whether that evidence is sufficient for a named contract scope.

### Examples

- A schema validator can PASS the shape of product.json.
- That PASS does not prove the Product's runtime realization or owner admission.

## Applicability

An Evaluation against declared validation criteria that produces a Validation Receipt for an exact subject, profile, inputs, and evaluation environment.

### Exclusions

- Semantic truth beyond the declared checks.
- Conformance outside the profile's complete coverage.
- Admission, acceptance, implementation, publication, or deployment authority.

## Boundaries

- Validation is a specialized Evaluation.
- Validation PASS is not automatically Conformance.
- Validation is not Admission, Acceptance, Publication, or Runtime Evidence.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.evaluation.definition/v1 | whole-json | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| domainspec-core:CAV2-D56 | lines:4116-4223 | `b675ec6ad0949edb8d8527ec3f352422889916f39aa74825269b7f81487f14ed` | `candidate-unadmitted` |

## Primary consumers

- cal.definition.conformance
- cal.definition.validation-receipt
- CAL-CML07-CRAFT-IDENTITY-CHAIN-0002

## Lookup and drift

- Index: `authority/definitions/candidates/0007-cml07-semantic-closure/DEFINITIONS-INDEX.md` / `cal.definition.validation@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0007-cml07-semantic-closure/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- SC-001

## Residue

None declared.

## Claim ceiling

This candidate defines Validation semantics only. It does not validate CML-07, establish conformance, or grant any authority effect.
