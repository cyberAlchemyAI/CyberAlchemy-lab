---
node_type: decision
is_session: false
status: active
boundary: INTERNAL — DomainSpec v2 authoring acceptance and merge control
created: 2026-08-24
decision_id: DEC-DSV2-VICTOR-PRE-MERGE-STRUCTURAL-APPROVAL
target_scope: all proposed merges whose changed paths include projects/domainspec-v2
source: direct owner statement, 2026-08-24
---

# Decision: Victor structural approval occurs before merge

## Decision

Rondelli is the DomainSpec v2 semantic and primary owner. Rondelli accepts
Define, Design, and Plan outputs and may authorize bounded implementation
through current Work Pack and Task Session controls.

Victor Boscaro is the distinct structural verifier. Victor's approval is not a
Define, Design, or Plan acceptance prerequisite. It is a blocking pre-merge
control over the exact merge candidate.

## Pre-merge rule

Every proposed merge whose changed-path set includes
`projects/domainspec-v2/**` must satisfy all of the following before merge:

1. Rondelli identifies the semantic decision or accepted work package and
   assigns the structural verification level required for the exact merge
   candidate.
2. The candidate is frozen by target branch, base and head identities, complete
   changed-byte inventory, validation-evidence bindings, and claim ceiling.
3. Victor independently issues an approval bound to that exact candidate and
   assigned verification level.
4. The pre-merge validator confirms the receipt, identities, inventory,
   validation bindings, and unchanged candidate bytes.
5. Any candidate-byte, base, head, target-branch, inventory, validation, claim-
   ceiling, or verification-level change invalidates the approval and requires
   a new Victor response.

The approval receipt is merge evidence. It is not part of the candidate it
approves and must not create a self-referential merge digest.

The validation mode is hybrid. The deterministic validator requires a direct
Victor-response evidence reference and digest, but it does not authenticate a
human principal. The merge owner must separately confirm that the referenced
evidence came directly from Victor before treating a passing structural result
as merge eligibility.

## Authority boundary

Victor verifies structural admissibility: identity, scope, exact bytes,
validation evidence, currentness, claim ceiling, and the assigned verification
level. Victor may block a structurally inadmissible merge package.

Victor does not acquire semantic ownership, change DomainSpec meaning, select
implementation behavior, discharge a ProofObligation, promote ontology,
authorize publication, release, deployment, or production use. Rondelli's
semantic acceptance does not substitute for Victor's distinct pre-merge
receipt.

## Examples

Accepted route:

```text
Rondelli accepts Design -> Plan -> bounded implementation and validation
-> exact merge candidate freezes
-> Rondelli assigns its verification level
-> Victor approves the exact candidate structurally
-> merge becomes eligible
```

Rejected routes:

```text
Victor must approve Design before planning can start
Rondelli's semantic acceptance is reused as Victor's structural approval
Victor approves, then candidate bytes change before merge
Victor's structural receipt is treated as ontology promotion or release authority
```

## Validation adapter

Rule `domainspec-v2-C12` is enforced by:

- `authority/pre-merge/pre-merge-structural-approval.v1.schema.json`;
- `authority/pre-merge/validate_pre_merge_structural_approval.py`; and
- `authority/pre-merge/test_validate_pre_merge_structural_approval.py`.

The validator is fail-closed. Absence of the receipt, a missing Victor identity,
an unassigned verification level, an incomplete changed-byte inventory, stale
validation evidence, or any exact-candidate mismatch blocks merge eligibility.
Its pass result is a structural-contract result, not actor-authentication proof.

## Historical boundary

This rule applies prospectively. Historical receipts remain evidence of their
original workflows and are not rewritten. Pending wording that required Victor
at an authoring-stage gate is superseded for future routing by this decision.

## Claim ceiling

Passing this gate proves only that Victor approved the exact structurally
validated merge candidate at the level assigned by Rondelli. It does not prove
the semantics correct, establish theorem truth or runtime conformance, promote
authority, publish, release, deploy, or create production effect.
