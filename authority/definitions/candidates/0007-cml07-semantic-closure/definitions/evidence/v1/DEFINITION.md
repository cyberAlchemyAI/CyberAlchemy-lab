<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Evidence

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.evidence`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:evidence-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

Evidence is a provenance-bound observation or record E associated with an explicit claim C, subject S, scope Q, and currentness condition. Its evidential force is limited to the declared relation support(E,C,S,Q); collection, existence, or volume does not establish sufficiency or authority.

```text
E = (evidence_id, claim_ref, subject_ref, provenance, scope, observed_at, currentness, content); exists(E) =/=> proves(C); supports(E,C,Q) only within Q.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| E | One evidence record. |
| C | The bounded claim that E may support or challenge. |
| Q | The declared scope and applicability conditions. |

### Boundary conditions

- Evidence must identify its claim, subject, provenance, and scope.
- Stale or mismatched evidence cannot silently support a current claim.
- Evidence assessment and authority decisions remain separate.

### Testable conditions

- The evidence identity and source are inspectable.
- The supported or challenged claim is explicit.
- The claim does not exceed the evidence scope.

## Plain-language voice

Evidence is something inspectable that bears on a specific claim. It can help prove or disprove that claim, but it does not decide by itself what is true or approved.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

CML-07 validation receipts, hostile fixtures, digest checks, and projection comparisons are evidence for particular checks. None can silently become admission or runtime proof.

### Examples

- A two-run byte comparison supports deterministic projection identity.
- A schema PASS supports shape evidence but does not prove Product meaning or runtime behavior.

## Applicability

An inspectable, provenance-bound record capable of supporting, weakening, or leaving unevaluable one explicit claim within a declared scope.

### Exclusions

- The claim itself.
- Automatic proof, truth, acceptance, admission, or authority.
- Unscoped output whose subject, origin, or applicability cannot be resolved.

## Boundaries

- Evidence is not Claim.
- Evidence is not Proof by mere existence.
- Evidence is not Decision, Authority, Admission, or Conformance without an applicable assessment.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| domainspec-core:CAV2-D38 | lines:2509-2571 | `8472c2f6b75902c8ce2a81ae1b3980657662d2b519571a948e43580f79889fb5` | `candidate-unadmitted` |
| domainspec-core:CAV2-D65 | lines:5092-5290 | `20ae1c5687973def6eb0b2cce1a96d44d8ecb45b64dd42fd461293dfe2b0bfdd` | `candidate-unadmitted` |

## Primary consumers

- cal.definition.evaluation
- cal.definition.validation
- cal.definition.conformance
- cal.definition.validation-receipt
- CAL-CML07-CRAFT-IDENTITY-CHAIN-0002

## Lookup and drift

- Index: `authority/definitions/candidates/0007-cml07-semantic-closure/DEFINITIONS-INDEX.md` / `cal.definition.evidence@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0007-cml07-semantic-closure/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- SC-001
- SC-002

## Residue

None declared.

## Claim ceiling

This candidate defines Evidence semantics only. It does not certify the adequacy of any evidence set or grant decision authority.
