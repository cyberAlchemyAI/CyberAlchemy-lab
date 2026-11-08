<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Retention Schedule

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.retention-schedule`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

A Retention Schedule is an owner-reviewed, versioned mapping from data class and purpose to trigger, expiry, deletion route and documented exception under the selected jurisdiction.

### Notation

No notation is required.

### Boundary conditions

- Software defaults cannot select a lawful retention duration.
- A schedule is not evidence that deletion ran successfully.

### Testable conditions

None declared.

## Plain-language voice

It states how long each kind of data is kept and what should happen when that time ends.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Retention Schedule meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One Challenge deployment and its data classes.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- Software defaults cannot select a lawful retention duration.
- A schedule is not evidence that deletion ran successfully.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/56 | `ee71e3997b38376b76da25a94a1bc4d9cc41a7b5470242f68e4aa7b5b02926dc` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- software/DEFINITION-COVERAGE.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.retention-schedule`
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
