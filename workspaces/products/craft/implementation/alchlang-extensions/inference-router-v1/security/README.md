# ISB-09 approved structural model

The owner replied **“approved”** to the preceding structural-model explanation.
The [decision record](STRUCTURAL-MODEL-APPROVAL.json) captures the approved model,
its exact normalized digest, approval context and remaining questions. This is
structural design approval. The [implementation report](IMPLEMENTATION.md) records the
local successor, interfaces, API flow, tests and remaining operational questions.

## Approved baseline

- Reuse Auth Foundation / Keycloak for authentication and Auth Foundation for authorization.
- Principals are either human users or services. Each may have memberships in multiple tenants.
- A tenant is a flat isolation boundary for membership, permissions, configuration and request data; no hierarchy or inherited access.
- Membership does not grant inference access. Current sessions, active roles and exact resource/action/tenant-scope permissions determine access.
- Application-defined actions are catalog `discover`, model `invoke` / `stream`, and routing strategy `use`.
- Retained keys are scoped by tenant, principal and idempotency key. Cached results are principal-private within the tenant and require current authorization before replay.
- Public model aliases are distinct from private provider bindings and credentials.
- Clients own presentation; authentication establishes identity; authorization evaluates access; Alch/DomainSpec owns application policy; native adapters own I/O and storage.

## Implementation

See the [implementation report](IMPLEMENTATION.md), [plan](PLAN.md),
[authored catalog filter](catalog.alch), [permission contract](requirement.alch)
and [source-bound evidence](evidence.json). Auth Foundation candidates are imported
by path; their frozen source and evidence are preserved. The shared service plan
still records security as its final implementation unit.

## Open Questions

The [implementation report](IMPLEMENTATION.md#open-questions) updates the original
decision questions. Interface binding is resolved; concrete production issuer,
client registration and policy/session operations remain deployment work. Disposable fixtures can support local construction. Tenant
hierarchy, delegated authority and cross-principal result sharing are outside
this approved baseline and require separate decisions if later requested.
