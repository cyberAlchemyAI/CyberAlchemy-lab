<!-- GENERATED FILE: canonical data is record.json. -->

# Typed Relation fixture

- Identity: `typed-relation:admission-transaction-materializes-project-state-example`
- Kind: `typed-relation`
- Lifecycle: `candidate`
- Owner: `role:relation-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "qualifiers": {
    "application_receipt_ref": "receipt:example",
    "consequence_role": "current-project-state",
    "output_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
  },
  "relation_evidence_refs": [
    "evidence:approval-admission-boundary-audit"
  ],
  "relation_kind_ref": "relation.materializes-consequence",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "admission-transaction",
    "ref": "admission-transaction:example",
    "version_ref": "admission-transaction:example@applied"
  },
  "target": {
    "kind": "project-state",
    "ref": "project-state:example",
    "version_ref": "project-state:example@decision-0074"
  }
}
```

## Declared relation roles


## Claim ceiling

Candidate schema witness only; it creates no relation, admission, authority, inference, runtime, or external effect.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
