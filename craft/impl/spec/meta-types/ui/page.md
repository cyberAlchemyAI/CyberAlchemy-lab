---
artifact_id: domainspec-v2-ui-page
artifact_type: development-profile-meta-type-card
companion_to: page.schema.yml
lifecycle_status: development-profile
authority_boundary: implementation-owned; not canonical DS-D1 authority
---

# Page

**Companion to** [`page.schema.yml`](./page.schema.yml).

## Formation Law

A terminal route owns primary content, layout/access context, and a rendered
unit inventory. Its `route_path`, `access_context`, `primary_content`,
`layout_ref`, and `unit_inventory` must contain non-whitespace text, while
`terminal` must be `true`.

## Distinguisher

A Page owns a terminal route and primary content; a Component is non-routable.
Add that route/content ownership or reroute the instance to Component.

## Graph And Authority Boundary

Page is source of `renders` and target of `wraps` and `protects` in the current
DS-D8 evidence slice. This development card neither activates DS-D1.15 nor
changes those relationships.
