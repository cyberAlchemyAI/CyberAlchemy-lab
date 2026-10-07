<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Measurement Method

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.measurement-method`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:measurement-method-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Measurement Method is a versioned reproducible procedure for measuring one declared property of a subject under stated conditions, with units, instruments or Tools, Implementation, calibration, sampling, computation, uncertainty treatment, evidence, applicability, owner, and failure boundaries. It is not a Measurement Result, Observation, metric value, Finding, Evidence Set, Decision, or authority rule.

```text
MeasurementMethod(x) => governed(x) and bounded(x); MeasurementMethod(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Measurement Method contract. |

### Boundary conditions

- Residue Measurement is one semantic use of Measurement Method; the positive Method Definition also supports other governed properties.
- Each execution binds exact subject, conditions, Method version, Tool and Implementation versions, and calibration state.
- Changing the procedure or uncertainty treatment requires a new Method version.

### Testable conditions

- Every Method names the measured property, unit system, procedure, conditions, calibration, sampling, computation, uncertainty, evidence, and failure contract.
- Repeated execution under declared equivalent conditions has a stated reproducibility criterion.
- No result or conclusion is inferred from the Method specification alone.

## Plain-language voice

A Measurement Method is a versioned reproducible procedure for measuring one declared property of a subject under stated conditions, with units, instruments or Tools, Implementation, calibration, sampling, computation, uncertainty treatment, evidence, applicability, owner, and failure boundaries. It is not a Measurement Result, Observation, metric value, Finding, Evidence Set, Decision, or authority rule.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

Measurement Method receives its own positive meaning so its carrier no longer borrows a broader Definition as its primary semantic identity.

### Examples

- method:residue-entropy/v2 defines how to calculate entropy over a typed residue register, including sampling window, formula, implementation digest, calibration fixture, and uncertainty rule.

## Applicability

A Measurement Method is a versioned reproducible procedure for measuring one declared property of a subject under stated conditions, with units, instruments or Tools, Implementation, calibration, sampling, computation, uncertainty treatment, evidence, applicability, owner, and failure boundaries.

### Exclusions

- It is not a Measurement Result, Observation, metric value, Finding, Evidence Set, Decision, or authority rule.
- Method admission does not prove calibration, correct execution, suitability for a subject, or acceptance of a result.
- This Definition does not admit a carrier, instance, relation, runtime, consumer, publication, or deployment.

## Boundaries

- Residue Measurement is one semantic use of Measurement Method; the positive Method Definition also supports other governed properties.
- Each execution binds exact subject, conditions, Method version, Tool and Implementation versions, and calibration state.
- Changing the procedure or uncertainty treatment requires a new Method version.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.step3.remaining | whole-file | `9e80895df1887113cfc407de6ed4d11f6cd37d4ac10857389ee060e1139c9f36` | `candidate-unadmitted` |

## Primary consumers

- CAL-DEFINITION-SPECIALIZATION-RESOLUTION-0014

## Lookup and drift

- Index: `authority/definitions/candidates/0014-definition-specialization-resolution/DEFINITIONS-INDEX.md` / `cal.definition.measurement-method@1.0.0-candidate.1`
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

This candidate defines Measurement Method for Step 3 review only and has no admission or downstream activation effect.
