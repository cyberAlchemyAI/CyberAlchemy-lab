<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Criterion Rating

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.criterion-rating`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

A Criterion Rating is one anchored judgment about one elicited rubric dimension of one response, made by an identified rater or pinned scorer with cited answer evidence and an explicit missingness state.

```text
Y[i,s,c,d,r,m,v] in {0,1,2,3,4,NA,UNK}
```

### Notation

| Symbol | Meaning |
| --- | --- |
| i | participant |
| s | session |
| c | case version |
| d | rubric dimension |
| r | rater or scorer configuration |
| m | response mode |
| v | score version |
| NA | dimension not fairly elicited |
| UNK | evidence missing or unusable |

### Boundary conditions

- A rating is an observation under a rubric, not a direct measure of a stable trait.
- Not elicited and unknown evidence must not be converted to zero.

### Testable conditions

None declared.

## Plain-language voice

The rating describes what this answer showed on this criterion under these exact conditions.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Criterion Rating meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One response, dimension, case version, rater, mode and score version.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- A rating is an observation under a rubric, not a direct measure of a stable trait.
- Not elicited and unknown evidence must not be converted to zero.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/18 | `01240396a11b626ef8f0302869e49cee2e60f3131f81ac5a80054fe1d988871b` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- research/full-protocol.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.criterion-rating`
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
