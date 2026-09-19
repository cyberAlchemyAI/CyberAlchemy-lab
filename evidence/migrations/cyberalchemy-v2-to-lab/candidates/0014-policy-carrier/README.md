# Policy carrier

Challenge -> exact policy, scope and subject -> allowed mode -> blocking questions -> owner review route.

A Policy defines scoped decision or behavior constraints through an exact profile. This carrier comes from the Lab's accepted normalization. Its concrete source example is Contestability Policy: a challenge contract that names the response, admissible modes, contradiction and validation links, owner route, resolution gate, blocking questions and unresolved-challenge route.

All required answers true -> ready for owner review. Any answer false -> blocked. Missing answers without a false answer -> indeterminate. A false answer remains blocking even when other answers are missing. Scope, subject or policy mismatches produce not-applicable; an undeclared mode produces unsupported-mode. These outcomes do not suggest a route outside the matching policy.

A resolution gate is the named check that must decide the challenge. The challenge residue route identifies where unresolved issues go. Neither is executed by this checker. Ready for review does not mean resolved, permitted or approved.

The implemented profile uses explicit boolean answers to nonempty blocking questions, with no coercion. Unknown answer keys, duplicate question identities and a link assigned both contradiction and validation roles are rejected. This is a bounded profile, not a general policy engine: other policy profiles and challenge contracts without blocking questions remain unsupported.

Answers are supplied assertions, not authenticated evidence. Subject and route references are opaque identities, not verified ownership or exact content bindings. Link identities are retained without resolving their targets. Object confidence and object residue are excluded from this record. No verdict, confidence update, gate completion or action authority is inferred.

Run from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0014-policy-carrier/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0014-policy-carrier/check.py evidence/migrations/cyberalchemy-v2-to-lab/candidates/0014-policy-carrier/artifact-types/policy/v1/fixtures/valid/policy-record.json evidence/migrations/cyberalchemy-v2-to-lab/candidates/0014-policy-carrier/examples/ready.json
```

CLI status 0 means ready for review, 1 means another valid preview outcome, and 2 means invalid input.

Validation passes 16 behavioral tests and 8 invalid contract fixtures. It verifies the normalization target, 28 Definition dependencies and their 26 source sections, preserving eight inherited source-lineage residues and the existing narrow D53 binding. Generated files reproduce and the predecessor snapshot remains unchanged.

The 195-target ledger now has 13 admitted targets, 88 constructed candidates and 94 remaining scaffolds. Next: `type.authority-model`.

The user's `next` authorizes construction and testing. A later adoption would approve applying an exact policy in a named scope, including its challenge modes, owner route and resolution gate. This candidate grants no adoption or permission to act.
