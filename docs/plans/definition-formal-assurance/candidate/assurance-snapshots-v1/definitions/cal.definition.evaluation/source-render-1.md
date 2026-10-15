<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Evaluation

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.evaluation`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:evaluation-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

An Evaluation applies a version-exact profile P to a version-exact subject S and input state I, yielding a complete outcome set O with causal blockers preserved. Evaluation is an evidence-producing process; its outcomes do not exceed P's declared coverage or create authority.

```text
evaluate(P@digest, S@digest, I@digest) -> O = {(check_id, PASS|FAIL|NOT_EVALUABLE, evidence_refs, blockers)}; O =/=> admitted(S).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| P | The exact evaluation profile. |
| S | The exact subject evaluated. |
| O | The collect-all set of declared check outcomes. |

### Boundary conditions

- The profile, subject, and inputs are exact and current.
- Dependent checks are recorded as NOT_EVALUABLE rather than omitted.
- An evaluation result remains inside the profile's coverage.

### Testable conditions

- Every declared check has an outcome.
- Every NOT_EVALUABLE outcome names its causal blocker.
- The evaluation identifies exact profile and subject digests.

## Plain-language voice

An Evaluation runs a declared set of checks against exact inputs and records every result, including the checks that could not yet be evaluated.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

CML-07 uses collect-all evaluations to expose all schema, reference, projection, and dependency outcomes before the one configured owner boundary.

### Examples

- An Artifact Type evaluation records schema and semantic-reference checks.
- A blocked source dependency makes dependent checks NOT_EVALUABLE, not absent or PASS.

## Applicability

The application of one exact evaluation profile to one exact subject and input state, collecting every declared check outcome and causal dependency.

### Exclusions

- A claim that the subject conforms.
- A human admission or acceptance decision.
- An effectful execution not explicitly included in the profile.

## Boundaries

- Evaluation is not Validation unless its profile is a validation profile.
- Evaluation is not Conformance determination.
- Evaluation output is not an authority decision.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.evaluation.definition/v1 | whole-json | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| domainspec-core:CAV2-D38 | lines:2509-2571 | `8472c2f6b75902c8ce2a81ae1b3980657662d2b519571a948e43580f79889fb5` | `candidate-unadmitted` |

## Primary consumers

- cal.definition.validation
- cal.definition.validation-receipt
- CAL-CML07-CRAFT-IDENTITY-CHAIN-0002

## Lookup and drift

- Index: `authority/definitions/candidates/0007-cml07-semantic-closure/DEFINITIONS-INDEX.md` / `cal.definition.evaluation@1.0.0-candidate.1`
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

This candidate defines Evaluation semantics only. It neither performs an evaluation nor determines conformance or admission.
