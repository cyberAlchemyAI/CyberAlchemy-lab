# DomainSpec v2 TOP-03 Shared-Syntax Adoption Acceptance Receipt

Status: accepted
Decision timestamp: 2026-08-22T13:55:34Z
Owner: repository owner (Boscaro), acting as DomainSpec v2 owner
Owner namespace: `domainspec`
Owner ID: `domainspec-v2-owner`
Route: `decision-gate`
Proposed decision ID: `DOMAINSPEC-V2-TOP03-ADOPTION-002`
Selected option: `DSV2-SOT-ACCEPT-AND-MIGRATE`

## Decision

The DomainSpec v2 owner adopts the exact CAV2-owned structural address syntax
identified below for references that cross the DomainSpec/CAV2 boundary.

DomainSpec v2 is the current DomainSpec source of truth. Frozen DomainSpec v1
material under `implementation/domainspec/` is historical evidence only and is
not a current source for proof-substrate meanings, owner decisions, lifecycle,
or future writes.

DomainSpec v2 retains all DomainSpec meanings, record kinds, relations,
evaluation inputs, obligation lifecycle, proof rules, and discharge decisions.
This adoption transfers none of that authority to CAV2.

## Exact Bindings

```yaml
decision_status: accepted
decision_timestamp: 2026-08-22T13:55:34Z
decision_owner_namespace: domainspec
decision_owner_id: domainspec-v2-owner
candidate_binding:
  path: projects/domainspec-v2/development/proof-obligation-substrate/2026-08-22-top03-shared-syntax-adoption-candidate.md
  digest:
    algorithm: sha256
    value: c9e072b557ded19996be9e44a8f7f983021083471425bf2fcdd14a084a598498
owner_route_binding:
  owner_namespace: domainspec
  id: domainspec-v2-authority-model
  version: worktree-2026-08-22
  source_path: projects/domainspec-v2/authority/AUTHORITY-MODEL.md
  selector: "# Authority Model"
  digest_scope: full-file-raw-bytes
  digest:
    algorithm: sha256
    value: a6080927d265c2064792acca788548dbdea2497e767d822730b7d616e663f073
syntax_binding:
  owner_namespace: cyberalchemy-v2
  id: proof-obligation-address-envelope
  version: 1.0.0
  source_path: cyberAlchemy-v2/authority/schemas/proof-obligation-address-envelope.v1.schema.json
  schema_uri: urn:cav2:proof-obligation-address-envelope:1.0.0
  digest:
    algorithm: sha256
    value: a3363314bc5c51a4ef5db559393553e41a9d43b43e3037442267fd9da7e3a078
accepted_adoption_scope: cross-project-structural-addressing-only
authority_effect: none-transferred
adoption_effect: accepted-for-domainspec-v2-cross-boundary-addressing
publication_effect: none
```

## Exact Claim Ceiling

DomainSpec v2 adoption accepts only the exact syntax version and structural
checks named above. It does not transfer DomainSpec meaning or lifecycle
authority to CAV2; grant CAV2 ownership of DomainSpec records; resolve an
obligation; establish proof truth; validate an evaluator; promote authority;
attest identity or truth; classify material; choose an audience; authorize
publication; or imply any adoption beyond the exact scope above.

Schema conformance establishes structural conformance only.

## Decision Evidence

- Owner source: direct user selection `1` in the DomainSpec v2 source-of-truth
  migration gate.
- Admissibility request:
  `research/2026-08-20-domainspec-v2-cav2-proof-obligation-substrate/development/refinement-runs/20260821T145409Z-proof-substrate-next-steps/stages/10-gate-01-top03-refresh/apply-corrected/owner-decisions/domainspec-v2-source-of-truth-option-admissibility-request.json`
  at SHA-256
  `0bb2cf23cfe2a05054edda6a813bdafe24ad0dafdf4409ccbc62c643e0e72008`.
- Admissibility receipt:
  `research/2026-08-20-domainspec-v2-cav2-proof-obligation-substrate/development/refinement-runs/20260821T145409Z-proof-substrate-next-steps/stages/10-gate-01-top03-refresh/apply-corrected/owner-decisions/domainspec-v2-source-of-truth-option-admissibility-receipt.json`
  at SHA-256
  `74cb758022547a00e96aa8d1e3bf2a3827d9a74e38ea8587adca9e0ca51bfdc0`.
- CAV2 owner acceptance:
  `cyberAlchemy-v2/authority/decisions/2026-08-22-top03-shared-syntax-owner-acceptance.md`
  at SHA-256
  `41311be32e366fcc7fffc4429a4a86d634d489e31cecd7b07c511aa4aa1b07d4`.
- Superseded DomainSpec v1 acceptance:
  `implementation/domainspec/docs/decisions/2026-08-22-top03-shared-syntax-adoption-acceptance.md`
  at SHA-256
  `e11a175cb612c5ac2486e9068cd1168760d803c4667e9bd2c27cd3f8ac7c3d08`.

## Supersession And Source Boundary

This receipt supersedes the DomainSpec v1 acceptance identified above. The old
receipt and candidate may be removed after a refreshed GATE-01 decision binds
this receipt. Their paths and digests remain historical evidence, but they have
no current routing or authority effect.

Future DomainSpec proof-substrate writes and semantic consultations must use
`projects/domainspec-v2/`. DomainSpec v1 may be consulted only when a task
explicitly asks for historical migration evidence; it may never decide current
DomainSpec v2 meaning.

This receipt has no scheduled expiration. It becomes invalid for routing if
the candidate, syntax schema, DomainSpec v2 authority model, claim ceiling, or
accepted scope changes.

This receipt does not authorize obligation discharge, proof claims,
publication, Git staging, commit, push, promotion, release, deployment, or
production use.
