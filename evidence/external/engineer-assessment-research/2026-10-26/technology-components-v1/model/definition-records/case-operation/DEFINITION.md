<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Question Lifecycle Operation

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.case-operation`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

A Question Lifecycle Operation is one idempotent or explicitly non-repeatable action with defined actor, input preconditions, state transition, output records and refusal or retry behavior in the case bank.

### Notation

No notation is required.

### Boundary conditions

- An operation's success receipt is not scientific validation of the case.
- An operation cannot grant owner authority absent an exact prior decision.

### Testable conditions

None declared.

## Plain-language voice

It is one concrete action, such as screening a draft or releasing an exact case version.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Question Lifecycle Operation meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One bounded executable step in the question lifecycle.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- An operation's success receipt is not scientific validation of the case.
- An operation cannot grant owner authority absent an exact prior decision.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/72 | `ee71e3997b38376b76da25a94a1bc4d9cc41a7b5470242f68e4aa7b5b02926dc` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- software/QUESTION-LIFECYCLE.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.case-operation`
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
