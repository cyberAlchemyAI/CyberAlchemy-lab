<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Application Access Permission

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.access-permission`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

An Application Access Permission is one versioned allow rule for an authenticated principal with an active role assignment to attempt a named action on a resource under exact subject, purpose, state and decision guards, with default denial otherwise.

### Notation

No notation is required.

### Boundary conditions

- A permission entry is an application enforcement rule, not a Lab Authority claim or owner decision.
- Role membership alone does not satisfy purpose, object or separation-of-duties guards.

### Testable conditions

None declared.

## Plain-language voice

It states which action the app may allow after checking who, which record, why and under which approved state.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Application Access Permission meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One MVP policy version, action and resource class.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- A permission entry is an application enforcement rule, not a Lab Authority claim or owner decision.
- Role membership alone does not satisfy purpose, object or separation-of-duties guards.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/74 | `9b4acc6f96f4cf70495aaabdba3ad6da6642f93890c7515c57248765a6272649` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- software/DEFINITION-COVERAGE.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.access-permission`
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
