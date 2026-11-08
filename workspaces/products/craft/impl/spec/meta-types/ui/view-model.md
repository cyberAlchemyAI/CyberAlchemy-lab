---
artifact_id: domainspec-v2-ui-view-model
artifact_type: development-profile-meta-type-card
companion_to: view-model.schema.yml
lifecycle_status: development-profile
authority_boundary: implementation-owned; not canonical DS-D1 authority
---

# View Model

**Companion to** [`view-model.schema.yml`](./view-model.schema.yml).

## Formation Law

A typed display-scoped shape declares nonempty fields, source references,
display context, and display roles, with `domain_authority=false`.

## Distinguisher

A View Model is display-scoped and non-authoritative; a Value Object owns
domain equality. Add source-backed display structure or reroute domain equality
to Value Object.

## Graph And Authority Boundary

View Model is source of `derives` and target of `shapes` and `displays` in the
current DS-D8 evidence slice. `shapes` endpoint reconciliation remains owner
residue; this card does not activate DS-D1.18.
