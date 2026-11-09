<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Session Event

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.session-event`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

A Session Event is an append-only, server-timed observation or accepted transition in one Session, with sequence, actor, purpose and causal parent sufficient to replay delivery and failure history.

### Notation

No notation is required.

### Boundary conditions

- An event log is not the answer recording.
- Client timestamps are diagnostic and cannot silently override server order.

### Testable conditions

None declared.

## Plain-language voice

It records when the case was shown, started, revealed, stopped or failed.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Session Event meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One session state or reveal occurrence.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- An event log is not the answer recording.
- Client timestamps are diagnostic and cannot silently override server order.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/48 | `ee71e3997b38376b76da25a94a1bc4d9cc41a7b5470242f68e4aa7b5b02926dc` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- software/DEFINITION-COVERAGE.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.session-event`
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
