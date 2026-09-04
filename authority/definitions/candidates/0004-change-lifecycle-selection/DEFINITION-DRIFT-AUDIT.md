<!-- GENERATED FILE: edit drift-audit-postimage.json and run render.py. -->

# Change Lifecycle Definition drift audit

> Candidate evidence; this view is not canonical.

## Summary

- Candidate Definition Count: `3`
- Workflow Definitions Included: `0`
- Redundant Definitions Included: `0`
- Owner Decision Required: `True`

## Findings

### CL-OWNERSHIP-001 (ownership-collapse, resolved-in-candidate)

Candidate 0003 mixed cross-context change classification with Craft workflow interaction policy.

Target: `authority/definitions/candidates/0003-single-decision-checkpoint`

Remediation: Select only Semantic Epoch, Representation Revision, and Derived Refresh here; route workflow terms to the separate Craft candidate.

### CL-OWNERSHIP-002 (redundant-definition, resolved-by-reuse)

Authority Boundary lacks a distinct validation purpose beyond existing CyberAlchemy Authority and Gate definitions.

Target: `cal.definition.authority-boundary`

Remediation: Do not include it in this registry postimage; reuse CAV2-D34 and CAV2-D37 through explicit source admission before a Lab consumer depends on them.

## Claim ceiling

This audit records the ownership correction embodied by candidate 0004. It does not reject, delete, admit, or supersede candidate 0003 or any live Definition.
