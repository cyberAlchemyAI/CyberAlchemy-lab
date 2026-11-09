<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Media Upload Attempt

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.upload-attempt`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

A Media Upload Attempt is one resumable transfer of one captured response to a private media object, with server-owned object/upload identity, part receipts, declared and verified checksums, expiry, completion or abort state and causal session assignment.

### Notation

No notation is required.

### Boundary conditions

- A part receipt or completed transfer is not a verified Media Object.
- A resumed transfer does not restart the session clock or change the assigned Case Version.

### Testable conditions

None declared.

## Plain-language voice

It tracks which bytes reached storage so a broken connection can resume without recording a new answer.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Media Upload Attempt meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One transfer attempt for one response and object key.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- A part receipt or completed transfer is not a verified Media Object.
- A resumed transfer does not restart the session clock or change the assigned Case Version.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/80 | `01240396a11b626ef8f0302869e49cee2e60f3131f81ac5a80054fe1d988871b` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- software/DEFINITION-COVERAGE.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.upload-attempt`
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
