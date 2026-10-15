# Governed state inspection

Candidate Method; no admission or execution authority.

Identity: `method:lab-governed-state-inspection`
Version: `1.0.0-candidate.1`

## Scope

Read permitted Lab artifacts at one exact captured cut.

## Inputs

- selected read scope
- exact source profile and cut
- artifact selector and budgets

## Actions

- lab.status
- catalog.get
- artifact.query
- artifact.inspect

## Roles

- bounded reader

## Gates

- actual read authority
- exact source/dependency closure
- budget and cut validity

## Outputs

- bounded result with original body, effective admission evidence, lifecycle, typed relations and gaps

## Evidence Requirements

- source byte hashes
- query cut
- selected exact contract
- admission evidence when applicable

## Boundary

- read-only
- no admission
- no inferred action authority
- no durable Agent memory

## Residue Rule

Report unresolved or unavailable references explicitly; never manufacture an admitted result.

## Validation Rule

Cross-check the returned claims against pinned canonical bytes and independent admission evidence.

## Recomposition Rule

Combine bounded inspection results only for the same verified cut and scope; preserve each claim basis.

## Exact canonical body

```json
{
  "actions": [
    "lab.status",
    "catalog.get",
    "artifact.query",
    "artifact.inspect"
  ],
  "authority_effect": "none",
  "boundary": [
    "read-only",
    "no admission",
    "no inferred action authority",
    "no durable Agent memory"
  ],
  "evidence_refs": [],
  "evidence_requirements": [
    "source byte hashes",
    "query cut",
    "selected exact contract",
    "admission evidence when applicable"
  ],
  "gates": [
    "actual read authority",
    "exact source/dependency closure",
    "budget and cut validity"
  ],
  "inputs": [
    "selected read scope",
    "exact source profile and cut",
    "artifact selector and budgets"
  ],
  "kind": "method",
  "method_id": "method:lab-governed-state-inspection",
  "name": "Governed state inspection",
  "outputs": [
    "bounded result with original body, effective admission evidence, lifecycle, typed relations and gaps"
  ],
  "owner_ref": "role:repository-owner",
  "recomposition_rule": "Combine bounded inspection results only for the same verified cut and scope; preserve each claim basis.",
  "residue_rule": "Report unresolved or unavailable references explicitly; never manufacture an admitted result.",
  "roles": [
    "bounded reader"
  ],
  "schema_version": "cyberalchemy-lab-method/v1-candidate",
  "scope": "Read permitted Lab artifacts at one exact captured cut.",
  "semantic_definition_ref": "CAV2-D32@1.0.0-candidate.1",
  "status": "candidate-unadmitted",
  "validation_rule": "Cross-check the returned claims against pinned canonical bytes and independent admission evidence.",
  "version": "1.0.0-candidate.1"
}
```
