---
artifact_id: domainspec-v2-ui-form
artifact_type: development-profile-meta-type-card
companion_to: form.schema.yml
lifecycle_status: development-profile
authority_boundary: implementation-owned; not canonical DS-D1 authority
---

# Form

**Companion to** [`form.schema.yml`](./form.schema.yml).

## Formation Law

A typed input aggregate declares nonempty fields, validation and error
contracts, submission action, target interface, and error mapping.

## Distinguisher

A Form owns a field-validation-submission aggregate; a Component owns only
typed visual I/O. Add the full aggregate or reroute a passive visual unit to
Component.

## Graph And Authority Boundary

Form is source of `submits` and `contracts` in the current DS-D8 evidence
slice. This card does not activate DS-D1.20.
