# Asynchronous build prototype terms

Private candidate specializations of [local control-plane terms](../local-control-plane-v1/definitions.md). Canonical definitions remain owned by CyberAlchemy-v2 authority/definitions.

## AB-QUEUE: Pending build

Formal prototype meaning: a tenant/project revision durably accepted in `queued` or `building` state. At most eight such revisions exist globally and two per tenant. HTTP acceptance does not establish a ready artifact.

Plain language: an upload waiting for, or using, the compiler.

Alch context: source bytes and their digest are persisted before a 202 response; the existing Alch/DomainSpec compiler checks them later.

## AB-TURN: Tenant build turn

Formal prototype meaning: one claimed queued revision, with at most one active compiler. Among waiting tenants select the tenant least recently dispatched, breaking ties by its oldest queued sequence; within that tenant select its oldest queued revision.

Plain language: waiting users take turns; one user cannot keep jumping ahead.

Alch context: the SQLite journal records claims, preserving dispatch ordering across restart. This is scheduling fairness, not equal CPU time or a latency guarantee.

## AB-RECOVERY: Build recovery

Formal prototype meaning: retain queued revisions across restart; mark previously building revisions failed with BUILD_INTERRUPTED. Never infer readiness from leftover artifacts.

Plain language: resume the waiting list and clearly report interrupted compilation.

Alch context: no route is selected by queue acceptance or successful compilation; the existing explicit activation endpoint remains required.

## Open Questions

See [README](README.md#open-questions).
