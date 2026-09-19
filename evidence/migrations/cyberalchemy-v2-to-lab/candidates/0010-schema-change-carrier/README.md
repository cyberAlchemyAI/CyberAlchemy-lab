# Schema Change carrier

Old schema -> proposed schema -> original examples checked again -> supplied migration examples checked.

This candidate makes a schema change reviewable before adoption. It binds the exact contents of both versions, names the owner and reason, records rollout and rollback routes, and checks regression witnesses. A witness is a supplied example with explicit expected results.

The demonstration adds a required integer `revision` to artifact records. The original example conforms to the old schema and fails the new schema. The supplied example with revision 1 conforms to the new schema. Revision 1 is fixture data, not a migration instruction for real records.

`compatible-on-witnesses` means only that all supplied original examples pass the new schema. `breaking-on-witnesses` means at least one fails. Neither result proves compatibility for every consumer. The checker evaluates supplied migration outputs; it does not execute a migration, rollout, rollback or adoption.

Run from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0010-schema-change-carrier/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0010-schema-change-carrier/check.py evidence/migrations/cyberalchemy-v2-to-lab/candidates/0010-schema-change-carrier/artifact-types/schema-change/v1/fixtures/valid/schema-change-record.json
```

Validation passes 15 behavioral tests and 8 invalid contract fixtures, checks 27 Definition dependencies and 25 source sections, and preserves the eight inherited source-lineage residues and the narrow D53 source binding. Rebuilding reproduces the generated files. The predecessor snapshot remains unchanged.

The supported scope is the prior finite typed graph profile, with stable schema identity, scope and relative level. Routes and obligations are recorded text, not executable plans or evidence of completion. Full consumer inventory, universal compatibility and production rollback remain unproven.

The 195-target ledger now contains 13 admitted targets, 84 constructed candidates and 98 remaining scaffolds. Next: `type.method`.

The user's `do next` authorizes construction and testing of this candidate. Any later adoption would approve using a particular schema change in its named scope, including its compatibility limits and migration obligations. This batch grants no such adoption.
