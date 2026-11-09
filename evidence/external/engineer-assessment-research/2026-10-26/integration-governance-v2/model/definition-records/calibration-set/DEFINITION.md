<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Calibration Set

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.calibration-set`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

A Calibration Set is a versioned collection of responses and ratings assigned before validation to train raters, refine anchors, fit permitted scoring parameters and find failure cases.

### Notation

No notation is required.

### Boundary conditions

- Results on the Calibration Set are development evidence, not held-out validation.
- A response used to tune a model cannot later become untouched test evidence for that model.

### Testable conditions

None declared.

## Plain-language voice

This is where the scoring procedure is learned and repaired.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Calibration Set meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One development phase and pinned score version.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- Results on the Calibration Set are development evidence, not held-out validation.
- A response used to tune a model cannot later become untouched test evidence for that model.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/24 | `01240396a11b626ef8f0302869e49cee2e60f3131f81ac5a80054fe1d988871b` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- research/full-protocol.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.calibration-set`
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
