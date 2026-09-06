---
artifact_id: domainspec-v2-ui-component
artifact_type: development-profile-meta-type-card
companion_to: component.schema.yml
lifecycle_status: development-profile
authority_boundary: implementation-owned; not canonical DS-D1 authority
---

# Component

**Companion to** [`component.schema.yml`](./component.schema.yml).

## Formation Law

A narrow non-routable visual unit has nonempty typed inputs and outputs and
declares route, domain-data, validation, and access authority as `false`.

## Distinguisher

A Component lacks the specialized aggregate authority of Page, Form, Guard, or
State Indicator. Add typed I/O and explicit non-authority flags, or reroute the
specialized law to its named concept.

## Graph And Authority Boundary

The current DS-D8 evidence makes Component source of `composes`, `consumes`,
and `displays`, and target of `renders` and `composes`. This card does not
activate DS-D1.17.
