---
artifact_id: domainspec-v2-ui-hook
artifact_type: development-profile-meta-type-card
companion_to: hook.schema.yml
lifecycle_status: development-profile
authority_boundary: implementation-owned; not canonical DS-D1 authority
---

# Hook

**Companion to** [`hook.schema.yml`](./hook.schema.yml).

## Formation Law

A framework-neutral reactive contract has nonempty typed inputs, typed returns,
reactive behavior, lifecycle, and effects.

## Distinguisher

A Hook owns reactive lifecycle behavior; a Binding owns a durable endpoint and
cache record. Add neutral lifecycle structure or reroute endpoint records to
Binding and framework-only helpers to implementation vocabulary.

## Graph And Authority Boundary

Hook is target of `consumes` in the current DS-D8 evidence slice. This card
does not activate DS-D1.19 or invent a Hook-to-Binding relationship.
