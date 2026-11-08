<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Assessment Attempt

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.assessment-attempt`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

An Assessment Attempt is one participant's version-pinned scored journey under a Study Protocol, containing at most three ordered Session slots and a terminal completion, withdrawal or void state.

### Notation

No notation is required.

### Boundary conditions

- An attempt is not one Session or one Response.
- A retry must preserve its predecessor and reason rather than replace history.

### Testable conditions

None declared.

## Plain-language voice

It groups the three possible case sessions into one auditable challenge run.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Assessment Attempt meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One challenge participation; practice is separate.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- An attempt is not one Session or one Response.
- A retry must preserve its predecessor and reason rather than replace history.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/44 | `872f620092ad78fde583f97c710f94a0e17e8152032ab900965a26d1c97532b7` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- software/DEFINITION-COVERAGE.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.assessment-attempt`
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
