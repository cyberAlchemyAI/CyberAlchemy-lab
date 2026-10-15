# Required owner coverage for the final review

Status: implementation design candidate. Authority effect: none. No owner outcome selected.

## Objective

Prepare one complete review package while retaining every independently required owner voice. Candidate construction and checks can continue under the existing development authorization. R08 remains the final owner checkpoint after S02 closes the package.

## Actual gap

The frozen `review-package-v2` kernel verifies exact targets, ordered Decision cores, validation, examples and private/public review. Its `role_declared` check proves that a selected source mentions an owner role. It does not prove that the selected roles cover every governing requirement for the target and requested effect.

The plan's nine-class member matrix proposes review routing; all `current_owner_authority_verified` fields remain false. The legacy owner registry supplies twenty independently scoped bindings. Their scope prose cannot be converted into new permissions by guessing from role names. The D74 Authority Boundary is limited to its exact transaction. The generic repository owner, lab owner and `person:<vrondelli>` remain distinct identities until an exact governing source establishes a binding.

## Resolver contract

1. Read the exact proposal and its complete ordered Decision cores. Pin the source cut, target identity/revision/carrier/original bytes, operation and requested effect.
2. Resolve independently selected governing requirement sources. Each requirement must explicitly select its target or bounded target class, scope, effect and required role. A target's own `owner_ref`, caller-supplied role list or proposed Principal cannot establish this requirement.
3. Compile the complete required role set for each core. Preserve distinct roles even when one person may answer for several. Reject unknown target classes, ambiguous scope mappings, missing requirements and contradictory governing sources. Report exact gaps with their affected cores.
4. Route each required role to its exact Principal and governing binding. Preserve the original legacy scope restrictions. Proposed formal Role/RoleAssignment records are review targets; they do not prove current owner authority.
5. Materialize all required voices with pending outcomes. A single checkpoint may collect several independent member responses. The package records each core, role, Principal and authority basis separately.
6. Revalidate requirement sources, routing, current authority and the frozen package when resolving the checkpoint. A changed requirement, cut, target, scope, core, example or evidence invalidates the affected package. Admission applies only the complete authorized all-or-nothing envelope.

## Candidate versus current governance

A proposed machine-readable requirement policy may be authored and exercised in an isolated development fixture. Its results must disclose that basis. It cannot establish that the existing repository's complete required owner set has been resolved. Final package closure must supply current governing requirements or explicitly present missing governance as proposed targets together with the independently authorized owners needed to admit them.

Review preparation does not grant action dispatch, service activation, publication or deployment authority. A later operational action uses its own exact authorization, environment, scope, prerequisites and recovery contract. A genuinely new bounded Agent episode must have new identity, Assignment, source cut and owned keys; the expired original Assignment remains unchanged.

## Implementation sequence

1. Finish API25 export qualification using its full 134-case suite and independent actual stdio observations. Preserve the complete API24 failure record.
2. Implement the closed requirement resolver and its source adapters. Build explicit isolated examples for multiple roles, one Principal answering for several roles, missing governing coverage, identity mismatch, changed requirements and transaction-limited authority.
3. Retarget the review kernel to the exact selected API implementation and integrate `proposal.review`. Keep incomplete required owner coverage visible and blocking.
4. Complete the remaining API and S02 obligations before assembling R08. The original 46 criteria and 34 operations remain the scope; this design closes none by itself.

## Source locations

- `docs/plans/0010-lab-one-shot-execution/governance/member-matrix.json`
- `docs/plans/0010-lab-one-shot-execution/governance/continuation-contract.json`
- `docs/proposals/0008-lab-api-contracts/api-contracts.json`, `proposal.review` preconditions
- `product/lab/release-candidates/v1/interface/review-package-v2/review.py`
- `authority/owners/foundation-01/v1/candidates/0004-craft-identity/owners.json`
- `authority/admissions/governance-transaction-surface/v1/instances/governance/authority-boundary.json`
- `authority/admissions/governance-transaction-surface/v1/instances/governance/workflow-decision-profile.json`
- `authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/policy.json`

These sources require exact hash binding in the resolver's implementation context before any effect. This design records the missing checks and their required behavior; it does not admit a new governance rule.
