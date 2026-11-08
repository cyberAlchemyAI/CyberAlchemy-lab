<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Conformance

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.conformance`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:conformance-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

Conformance is a relation among an exact subject S, exact contract C, declared scope Q, applicable profile P, current evidence set E, and assessment owner. It may be asserted only when P declares E sufficient for every obligation in Q. Different conformance scopes remain orthogonal and cannot be inferred from one another.

```text
conforms(S@digest, C@digest, Q, P@version, E) only if complete(P,Q) and current(E) and satisfies(E, obligations(C,Q)); schema_conformance(S) =/=> identity_contract_conformance(S) =/=> implementation_conformance(S) =/=> runtime_conformance(S).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| S | The exact subject whose conformance is assessed. |
| C | The exact contract and version assessed. |
| Q | The bounded conformance scope. |
| E | The current evidence set used for the assessment. |

### Boundary conditions

- Subject, contract, scope, profile, evidence, and owner are explicit.
- Evidence stale against either subject or contract makes the claim not current.
- Schema, identity-contract, implementation, and runtime conformance are separate scopes.

### Testable conditions

- Every obligation in the declared scope maps to current evidence or a causal NOT_EVALUABLE result.
- No narrower conformance claim is promoted into a broader scope.
- A conformance assertion carries no admission or publication effect.

## Plain-language voice

Conformance says that one exact thing meets one exact contract for a clearly named scope, backed by enough current evidence. Passing a few checks—or matching a schema—does not automatically prove a broader kind of conformance.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

CML-07 may assess schema and identity-contract conformance for its identity artifacts. Implementation and runtime conformance remain deferred to later construction stages.

### Examples

- product.json can conform to the Product Identity schema without proving a runtime Product realization.
- An identity graph can satisfy endpoint and non-collapse obligations without admitting its artifacts.

## Applicability

A current, scoped, evidence-backed relation asserting that one exact subject satisfies one exact contract version under one applicable conformance profile.

### Exclusions

- A free-standing status label.
- A validator PASS without declared completeness for the conformance scope.
- Admission, semantic truth, implementation existence, runtime behavior, publication, or deployment authority.

## Boundaries

- Conformance is not Validation execution or a PASS label.
- Schema conformance is not Identity-contract, Implementation, or Runtime conformance.
- Conformance is not Admission, Acceptance, Authority, Publication, or Deployment.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| domainspec-core:CAV2-D38 | lines:2509-2571 | `8472c2f6b75902c8ce2a81ae1b3980657662d2b519571a948e43580f79889fb5` | `candidate-unadmitted` |
| domainspec-core:CAV2-D56 | lines:4116-4223 | `b675ec6ad0949edb8d8527ec3f352422889916f39aa74825269b7f81487f14ed` | `candidate-unadmitted` |
| domainspec-core:CAV2-D65 | lines:5092-5290 | `20ae1c5687973def6eb0b2cce1a96d44d8ecb45b64dd42fd461293dfe2b0bfdd` | `candidate-unadmitted` |

## Primary consumers

- CAL-CML07-CRAFT-IDENTITY-CHAIN-0002
- tests/conformance/cml07-craft-identity/schema-and-identity-contract/

## Lookup and drift

- Index: `authority/definitions/candidates/0007-cml07-semantic-closure/DEFINITIONS-INDEX.md` / `cal.definition.conformance@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0007-cml07-semantic-closure/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- SC-001

## Residue

- Implementation and runtime conformance remain deferred beyond CML-07.

## Claim ceiling

This candidate defines scoped Conformance semantics only. It establishes no conformance result for any subject and no authority effect.
