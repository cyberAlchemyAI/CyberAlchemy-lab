<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Analytics Event Specification

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.analytics-event-spec`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

An Analytics Event Specification is a versioned allowlist for one event name, trigger, emitter, purpose, permitted fields, deduplication rule, retention link and metric consumers.

### Notation

No notation is required.

### Boundary conditions

- It is not an event occurrence, a metric result, a research permission or a reason to log sensitive content.

### Testable conditions

None declared.

## Plain-language voice

The contract that says exactly when an event may be recorded and what it may contain.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Analytics Event Specification meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One operational observation kind and authorized processing context.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- It is not an event occurrence, a metric result, a research permission or a reason to log sensitive content.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/93 | `a4536650bdbfe53274017abd662b51804ad170ec0d41031688632bba971049bb` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- software/DEFINITION-COVERAGE.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.analytics-event-spec`
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
