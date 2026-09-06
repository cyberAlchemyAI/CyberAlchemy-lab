---
artifact_id: domainspec-v2-ui-layout
artifact_type: development-profile-meta-type-card
companion_to: layout.schema.yml
lifecycle_status: development-profile
authority_boundary: implementation-owned; not canonical DS-D1 authority
---

# Layout

**Companion to** [`layout.schema.yml`](./layout.schema.yml).

## Formation Law

A shell owns nonempty named `slots` and `shared_chrome`, contains no
page-specific primary content, and declares `wrap_target=Page`.

## Distinguisher

A Layout owns shell slots; a Page owns terminal primary content. Add finite
slots and the Page wrap target, or reroute primary-content ownership to Page.

## Graph And Authority Boundary

Layout is source of `wraps` in the current DS-D8 evidence slice. This card is a
development profile contract, not activation of DS-D1.16.
