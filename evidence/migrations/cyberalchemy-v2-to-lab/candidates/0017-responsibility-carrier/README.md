# Responsibility carrier

Named owner -> scoped obligation -> exact evidence checks -> review or escalation.

Responsibility is an owner-qualified obligation to perform, maintain, answer for or route an outcome. It does not grant the authority needed to cause that outcome. This candidate keeps Responsibility distinct from Authority and Authority Claim and preserves both normalized D34/D69 source selectors.

The example makes a maintainer accountable for reviewable validation evidence for an exact candidate. Its criteria inspect the validation record's reported result and authority effect. Those field checks are deliberately narrower than proving that all validation ran or that the obligation is complete.

Each observation binds the exact responsibility record and subject by content hash. Each supplied criterion evidence file is also hash-bound. Duplicate or unknown criterion evidence, changed files and mismatched subjects are rejected. Values compare without coercion: booleans, integers and strings remain distinct.

All fields match -> supported for owner review. Any field contradicts its expected value -> unmet. Missing evidence or a missing field -> indeterminate. An unmet criterion takes precedence over missing evidence, while both remain visible. Scope mismatches are not applicable and suggest no route.

Supported results name the review route. Unmet or indeterminate results name the escalation route, meaning where unresolved work should be taken. Neither route is executed. Every result leaves completion acceptance, owner authentication and action authorization false.

This bounded profile checks top-level JSON fields against explicit string, integer or boolean values. It does not authenticate owners, assess evidence relevance or truth, verify that evidence concerns the bound subject, prove actual outcomes, manage deadlines, delegate work or accept completion. The synthetic failing-evidence example is labeled fixture-only. Team and governance authority remain separate work.

Run from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0017-responsibility-carrier/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0017-responsibility-carrier/check.py evidence/migrations/cyberalchemy-v2-to-lab/candidates/0017-responsibility-carrier/artifact-types/responsibility/v1/fixtures/valid/responsibility-record.json evidence/migrations/cyberalchemy-v2-to-lab/candidates/0017-responsibility-carrier/examples/supported.json
```

CLI status 0 means supported for owner review, 1 means unmet, indeterminate or not applicable, and 2 means invalid input. Status 0 is not accepted completion.

Validation passes 16 behavioral tests and 8 invalid contract fixtures. It verifies 27 Definition dependencies and their 25 source sections, both normalized D34/D69 selectors, eight inherited source-lineage residues and the existing narrow D53 binding. Generated files reproduce and the predecessor snapshot remains unchanged.

The 195-target ledger now has 13 admitted targets, 91 constructed candidates and 91 remaining scaffolds. Next: `type.gate`.

The user's `next` authorizes construction and testing. A later responsibility assignment would approve a particular owner's obligation in a named scope, its evidence requirements and escalation route. Completion acceptance and authority to act remain separate decisions.
