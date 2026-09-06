---
artifact_id: domainspec-v2-ui-binding
artifact_type: development-profile-meta-type-card
companion_to: binding.schema.yml
lifecycle_status: development-profile
authority_boundary: implementation-owned; not canonical DS-D1 authority
---

# Binding

**Companion to** [`binding.schema.yml`](./binding.schema.yml).

## Formation Law

A Binding node is a durable integration record with nonempty endpoint mode,
target, trigger, parameter/result mappings, cache key, and invalidation.

## Distinguisher

A Binding is a durable record with endpoint/cache structure; a pure connection
remains a DS-D8 relationship. An edge-only connection must never be coerced
into a Binding node.

## Graph And Authority Boundary

Binding is source of `fetches` and `mutates` in the current DS-D8 evidence
slice. The Hook-Binding relationship request remains owner residue; this card
does not activate DS-D1.23.
