<!-- GENERATED FILE: edit drift-audit-postimage.json and run render.py. -->

# Craft Workflow Interaction Definition drift audit

> Candidate evidence; this view is not canonical.

## Summary

- Candidate Definition Count: `5`
- Stable Legacy Ids Preserved: `1`
- External Source Admissions Open: `5`
- Owner Bindings Open: `1`
- Bounded Contexts Inferred: `0`

## Findings

### CW-001 (ownership-misclassification, resolved-in-candidate)

Workflow placement policy was previously scoped as shared CyberAlchemy Lab governance.

Target: `candidate 0003 workflow-interaction definitions`

Remediation: Use Craft-owned definition IDs and role ownership while retaining shared Authority and Gate as external dependencies.

### CW-002 (terminology-collapse, resolved-in-candidate)

Decision Bundle mixed interaction presentation with governance aggregation.

Target: `Decision Bundle`

Remediation: Use Decision Request Set for presentation only; each member remains an independently governed decision.

### CW-003 (source-admission, open)

The five exact CyberAlchemy-v2 and DomainSpec/Craft selectors are current but unadmitted in CyberAlchemy Lab.

Target: `external source bindings`

Remediation: Obtain source-admission decisions before promotion review.

### CW-004 (owner-binding, open)

The selected architecture names the role, but the admitted Lab owner registry does not bind it to an accountable principal.

Target: `role:craft-product-owner`

Remediation: Bind the exact role and scope without collapsing it into definition-owner authority.

## Claim ceiling

This audit records candidate ownership correction and open dependencies. It does not admit Craft vocabulary or select a bounded context.
