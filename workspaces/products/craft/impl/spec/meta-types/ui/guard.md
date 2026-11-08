---
artifact_id: domainspec-v2-ui-guard
artifact_type: development-profile-meta-type-card
companion_to: guard.schema.yml
lifecycle_status: development-profile
authority_boundary: implementation-owned; not canonical DS-D1 authority
---

# Guard

**Companion to** [`guard.schema.yml`](./guard.schema.yml).

## Formation Law

A non-authoritative UI gate declares nonempty protected surface, source Rule,
conditions, fallback, and enforcement scope, with
`decision_authority=false`.

## Distinguisher

A Guard projects an authoritative Rule into UI behavior; it never owns the
access decision. Add source/fallback/non-authority structure or reroute the
decision to Rule.

## Graph And Authority Boundary

Guard is source of `protects` and `mirrors` in the current DS-D8 evidence
slice. Component target scope remains owner residue; this card does not
activate DS-D1.22.
