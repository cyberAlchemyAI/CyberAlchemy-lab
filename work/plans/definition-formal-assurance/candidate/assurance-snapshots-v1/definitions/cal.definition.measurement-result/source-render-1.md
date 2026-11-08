<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Measurement Result

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.measurement-result`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:measurement-result-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Measurement Result is an immutable attributable record of one exact Measurement Method execution against one exact subject revision under declared conditions, preserving values, units, uncertainty, raw evidence, Tool and Implementation versions, timestamps, validity posture, owner, and receipt. It is not the Measurement Method, subject, Observation narrative, Evidence Set, Finding, causal claim, Decision, accepted fact, or authority effect.

```text
MeasurementResult(x) => governed(x) and bounded(x); MeasurementResult(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Measurement Result contract. |

### Boundary conditions

- The Method defines how measurement is performed; the Result records what one execution produced.
- Corrections create successor Results while preserving the original record and evidence.
- Interpretation, acceptance, and use in a Finding remain separate governed acts.

### Testable conditions

- Every Result resolves one exact Method version, subject revision, execution interval, conditions, values, units, uncertainty, evidence, and receipt.
- Result validity posture is explicit and independent from support for any claim.
- No Measurement Result silently changes after recording.

## Plain-language voice

A Measurement Result is an immutable attributable record of one exact Measurement Method execution against one exact subject revision under declared conditions, preserving values, units, uncertainty, raw evidence, Tool and Implementation versions, timestamps, validity posture, owner, and receipt. It is not the Measurement Method, subject, Observation narrative, Evidence Set, Finding, causal claim, Decision, accepted fact, or authority effect.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

Measurement Result receives its own positive meaning so its carrier no longer borrows a broader Definition as its primary semantic identity.

### Examples

- result:residue-entropy:run-44 records 0.37 bits for experiment-run:44 using method:residue-entropy/v2, its raw register digest, computation receipt, and ±0.02 uncertainty.

## Applicability

A Measurement Result is an immutable attributable record of one exact Measurement Method execution against one exact subject revision under declared conditions, preserving values, units, uncertainty, raw evidence, Tool and Implementation versions, timestamps, validity posture, owner, and receipt.

### Exclusions

- It is not the Measurement Method, subject, Observation narrative, Evidence Set, Finding, causal claim, Decision, accepted fact, or authority effect.
- A value without exact Method, subject, conditions, units, uncertainty, and provenance is not a conforming Measurement Result.
- This Definition does not admit a carrier, instance, relation, runtime, consumer, publication, or deployment.

## Boundaries

- The Method defines how measurement is performed; the Result records what one execution produced.
- Corrections create successor Results while preserving the original record and evidence.
- Interpretation, acceptance, and use in a Finding remain separate governed acts.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.step3.remaining | whole-file | `9e80895df1887113cfc407de6ed4d11f6cd37d4ac10857389ee060e1139c9f36` | `candidate-unadmitted` |

## Primary consumers

- CAL-DEFINITION-SPECIALIZATION-RESOLUTION-0014

## Lookup and drift

- Index: `authority/definitions/candidates/0014-definition-specialization-resolution/DEFINITIONS-INDEX.md` / `cal.definition.measurement-result@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0014-definition-specialization-resolution/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- authority/artifact-types/candidates/0005-remaining-18-complete-model/model.json
- .arcanum/ontology-vault/2026-10-06-lab-semantic-gap-audit.md

## Residue

- Definition-owner admission remains required.
- Artifact Type rebinding and admission remain separate.

## Claim ceiling

This candidate defines Measurement Result for Step 3 review only and has no admission or downstream activation effect.
