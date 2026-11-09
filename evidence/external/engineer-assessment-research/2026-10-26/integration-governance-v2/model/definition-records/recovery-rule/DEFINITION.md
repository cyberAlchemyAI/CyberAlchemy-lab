<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Session Recovery Rule

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.recovery-rule`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

A Session Recovery Rule is a versioned, state-specific prescription for one failure class under an Administration Policy, defining observable detection, what remains valid, timer behavior, same-assignment recovery eligibility, void/replacement criteria, participant message and required audit evidence.

### Notation

No notation is required.

### Boundary conditions

- A rule is not an observed failure or a runtime recovery decision.
- A replacement case must be a previously released form selected under the study protocol; a generator cannot authorize an immediate retry.

### Testable conditions

None declared.

## Plain-language voice

It says exactly what the product should preserve and do when a particular kind of failure occurs.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Session Recovery Rule meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One failure class, administration-policy version and session state.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- A rule is not an observed failure or a runtime recovery decision.
- A replacement case must be a previously released form selected under the study protocol; a generator cannot authorize an immediate retry.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/78 | `01240396a11b626ef8f0302869e49cee2e60f3131f81ac5a80054fe1d988871b` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- software/DEFINITION-COVERAGE.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.recovery-rule`
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
