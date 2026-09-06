<!-- GENERATED FILE: edit drift-audit-postimage.json and run render.py. -->

# Artifact Surface Foundation successor drift audit

> Candidate evidence; this view is not canonical.

## Summary

- Conflicting Consumers: `0`
- Review Defects: `4`
- Successor Definitions: `4`
- Undefined Critical Terms: `0`

## Findings

### ASF-REV-001 (required, resolved-in-successor)

Artifact Type Request candidate.1 contains a broken normative phrase.

Target: `authority/definitions/candidates/0010-artifact-surface-foundation-revision/definitions/artifact-type-request/v1/definition.json`

Remediation: Correct Q's non-identity with both subject artifact a and Artifact Type T.

### ASF-REV-002 (required, resolved-in-successor)

Artifact Type Resolution candidate.1 lacks an executable operation contract.

Target: `authority/definitions/candidates/0010-artifact-surface-foundation-revision/definitions/artifact-type-resolution/v1/definition.json`

Remediation: Require a reusable structured resolver with resolved, unresolved, and ambiguous outcomes.

### ASF-REV-003 (required, resolved-in-successor)

Canonical Package Manifest candidate.1 does not require its own role entry.

Target: `authority/definitions/candidates/0010-artifact-surface-foundation-revision/definitions/canonical-package-manifest/v1/definition.json`

Remediation: Require exactly one canonical package.json self-entry.

### ASF-REV-004 (required, resolved-in-product-candidate)

The selected-tree audit was authored as fixed findings instead of computed from exact subjects.

Target: `tooling/validators/artifact_surface_candidate_2.py`

Remediation: Compute the audit from an explicit plan, current bytes, and the reusable resolver.

## Claim ceiling

Candidate drift assessment only; resolved-in-successor does not mean admitted or activated.
