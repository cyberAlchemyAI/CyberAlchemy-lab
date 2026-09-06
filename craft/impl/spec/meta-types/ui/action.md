---
artifact_id: domainspec-v2-ui-action
artifact_type: development-profile-meta-type-card
companion_to: action.schema.yml
lifecycle_status: development-profile
authority_boundary: implementation-owned; not canonical DS-D1 authority
---

# Action

**Companion to** [`action.schema.yml`](./action.schema.yml).

## Formation Law

A named user intent declares nonempty trigger, target kind, effect boundary,
and observable success and error outcomes.

## Distinguisher

An Action owns a complete intent/outcome contract; a passive event handler does
not. Add that contract or keep the handler as implementation vocabulary.

## Graph And Authority Boundary

Action is target of `submits` in the current DS-D8 evidence slice. The missing
Action-source relationship remains owner residue; this card does not activate
DS-D1.21.
