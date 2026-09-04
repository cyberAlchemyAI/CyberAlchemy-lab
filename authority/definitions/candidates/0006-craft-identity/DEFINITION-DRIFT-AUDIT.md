<!-- GENERATED FILE: edit drift-audit-postimage.json and run render.py. -->

# Craft identity Definition drift audit

> Candidate evidence; this view is not canonical.

## Summary

- Candidate Definition Count: `6`
- Stable Legacy Ids Preserved: `4`
- New Lab Ids: `2`
- External Source Admissions Open: `8`
- Owner Bindings Open: `4`
- Bounded Contexts Inferred: `0`

## Findings

### CI-001 (source-admission, open)

The selected source bytes are current but their expanded CML-07 use is not admitted.

Target: `eight external selectors`

Remediation: Bind the exact admissions and Definition bytes in the final CML-07 decision boundary.

### CI-002 (owner-binding, open)

The candidate assigns four separate scopes to one principal, but those assignments are not active.

Target: `four identity owner roles`

Remediation: Admit the exact role assignments without collapsing their decision scopes.

### CI-003 (terminology-collapse, resolved-in-candidate)

Each concept now has an independent stable Definition identity and explicit non-collapse boundaries.

Target: `Product Project Method Goal Identity Relation`

Remediation: Reject future carriers that infer one identity from a directory, shared name, owner, or relation endpoint.

### CI-004 (successor-blocker, open)

Identity carrier Artifact Types have not been authored.

Target: `CML07-S2`

Remediation: After W0 admission, author schema-first carrier contracts without changing these Definition epochs for projection-only work.

## Claim ceiling

This audit reports candidate Definition drift and successor blockers only; it does not admit or instantiate any artifact.
