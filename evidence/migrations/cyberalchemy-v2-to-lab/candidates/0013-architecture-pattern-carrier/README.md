# Architecture Pattern carrier

Recurring design problem -> forces -> reusable response -> consequences -> applicability and structure checks.

An Architecture Pattern records a reusable design response and its tradeoffs. A force is a pressure the design must address, such as preserving history or limiting storage growth. A consequence is a benefit, cost or risk of the response. Every declared force must be addressed by a consequence.

The carrier is a supporting target in the Lab's accepted normalization, rather than a directly imported legacy Definition. Its concrete example binds the reconstructed Append-Only Event Ledger Definition. That example does not define every architecture pattern.

Existing events -> append new events -> preserve earlier history.

The bounded checker compares two supplied ledger snapshots. It verifies scope, unique event identities, integer sequences starting at one and an unchanged earlier event prefix. An unchanged snapshot is allowed. JSON object key order and whitespace do not affect prefix comparison; JSON value types remain distinct. The fixture is illustrative data, not an observation of production enforcement.

Matching declared context -> check snapshot conformance. Missing context -> indeterminate. Conflicting context -> not applicable. The last two outcomes never report conformance as true. Applicability uses exact string comparisons; it does not establish real-world suitability or evaluate free-text exclusions.

Only the append-only ledger snapshot profile is implemented, bounded to 10,000 events per snapshot. Passing does not prove runtime enforcement, durability, concurrent-writer correctness, projection correctness or pattern promotion. No code or ledger operation is executed.

Run from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0013-architecture-pattern-carrier/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0013-architecture-pattern-carrier/check.py evidence/migrations/cyberalchemy-v2-to-lab/candidates/0013-architecture-pattern-carrier/artifact-types/architecture-pattern/v1/fixtures/valid/architecture-pattern-record.json
```

The checker returns 0 for conformance, 1 for a violation or unestablished applicability, and 2 for invalid input.

Validation passes 16 behavioral tests and 8 invalid contract fixtures. It verifies the normalization target, six Definition dependencies and their six source sections, preserves three inherited source-lineage residues and verifies the existing D53 overlay. Generated files reproduce and the predecessor snapshot remains unchanged.

The 195-target ledger now has 13 admitted targets, 87 constructed candidates and 95 remaining scaffolds. Next: `type.policy`.

The user's `next` authorizes construction and testing. A later pattern adoption would approve using an exact design response in a named context, with its constraints and tradeoffs. This candidate grants no adoption or runtime authority.
