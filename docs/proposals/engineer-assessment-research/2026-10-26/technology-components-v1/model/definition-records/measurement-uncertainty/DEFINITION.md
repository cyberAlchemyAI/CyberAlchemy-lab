<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Measurement Uncertainty

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.measurement-uncertainty`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

Measurement Uncertainty is the estimated range or decision instability of a score arising from sampled cases, raters, response modes, transcription and model fit under a named measurement design.

```text
P(decision changes | plausible case, rater, mode replacements, design)
```

### Notation

| Symbol | Meaning |
| --- | --- |
| decision | predeclared classification or ranking action |
| design | actual number and allocation of cases, raters and modes |

### Boundary conditions

- Rater agreement alone is not total score uncertainty.
- An interval estimated with multiple research cases cannot be applied to a one-case product without a design study.

### Testable conditions

None declared.

## Plain-language voice

It asks whether a reasonable repeat of the assessment would lead to the same conclusion.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Measurement Uncertainty meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One score version, population and intended decision.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- Rater agreement alone is not total score uncertainty.
- An interval estimated with multiple research cases cannot be applied to a one-case product without a design study.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/23 | `ee71e3997b38376b76da25a94a1bc4d9cc41a7b5470242f68e4aa7b5b02926dc` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- research/full-protocol.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.measurement-uncertainty`
- Drift owner: `role:ea-definitions-owner-unassigned`
- Audit: `tools/validate_definition_records.py`
- Challenge route: `role:ea-independent-reviewer-unassigned`

## Typed relations

No typed relations declared.

## Evidence

None declared.

## Residue

None declared.

## Claim ceiling

Generated project-scoped candidate Definition record only. Shape and projection checks grant no Lab admission, semantic truth, implementation, collection or employment-use authority.
