<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Session Assignment

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.session-assignment`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

A Session Assignment is one immutable binding of an Attempt slot to a released Case Version, Rubric, Response Mode and Administration Policy, with any retry linked to its voided predecessor.

### Notation

No notation is required.

### Boundary conditions

- Assignment is not evidence that the participant viewed or answered the case.
- A retired case may remain pinned to historical answers but cannot receive new assignments.

### Testable conditions

None declared.

## Plain-language voice

It freezes the exact task and rules for one slot before the participant starts.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Session Assignment meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One scored slot and one administration instance.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- Assignment is not evidence that the participant viewed or answered the case.
- A retired case may remain pinned to historical answers but cannot receive new assignments.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/46 | `9b4acc6f96f4cf70495aaabdba3ad6da6642f93890c7515c57248765a6272649` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- software/DEFINITION-COVERAGE.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.session-assignment`
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
