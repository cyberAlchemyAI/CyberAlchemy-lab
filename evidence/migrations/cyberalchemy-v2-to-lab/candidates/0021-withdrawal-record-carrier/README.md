# Withdrawal Record carrier

Previously withdrawn identifier -> permanent reservation -> recorded successor -> reject attempted reuse.

The accepted normalization already lists twelve withdrawn identifiers, CAV2-D70 through CAV2-D81, with successors KEP-D1 through KEP-D12. This candidate preserves that complete list. It does not initiate a withdrawal or delete source material.

A reservation is a record that the retired name must not be recycled. The checker requires every normalized reservation exactly once, with its recorded successor and permanent-reservation flag. Omissions, duplicate retired IDs, changed successors and attempts to mark an identifier reusable are rejected.

Allocation queries bind the exact Withdrawal Record and name a scope. Proposed IDs are compared exactly against the retired names; surrounding whitespace is rejected rather than silently normalized. A collision returns blocked-reuse and the recorded successor. A scope mismatch returns not-applicable. No-listed-collision means only that the supplied names avoid this list; it does not prove global name availability or authorize allocation.

This carrier is supported directly by the accepted normalization. There is no standalone Withdrawal Record Definition binding asserted. That semantic foundation gap remains explicit rather than borrowing an unrelated Definition. The successor names are preserved as recorded references; their current authority and existence are not verified.

Permanent reservation is enforced locally against the bound normalization snapshot. This does not install a global allocator, guarantee future enforcement, retire anything new, transfer authority or admit a successor. The source repository and previous candidate snapshots remain unchanged.

Run from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0021-withdrawal-record-carrier/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0021-withdrawal-record-carrier/check.py evidence/migrations/cyberalchemy-v2-to-lab/candidates/0021-withdrawal-record-carrier/artifact-types/withdrawal-record/v1/fixtures/valid/withdrawal-record.json evidence/migrations/cyberalchemy-v2-to-lab/candidates/0021-withdrawal-record-carrier/examples/collision.json
```

CLI status 0 means no listed collision, 1 means blocked reuse or not applicable, and 2 means invalid input. Status 0 grants no allocation permission.

Validation passes 14 behavioral tests and 8 invalid contract fixtures. It verifies the exact normalization and supporting target, preserves predecessor evidence and checks the existing D53 overlay. No source Definition is newly bound by this batch. Generated files reproduce and the predecessor snapshot remains unchanged.

The 195-target ledger now has 13 admitted targets, 95 constructed candidates and 87 remaining scaffolds. Next: `type.residue`.

The user's `next` authorizes construction and testing. A later adoption would approve relying on this reservation contract to prevent reuse of the listed retired names. It would not initiate new withdrawals or confer authority on the named successors.
