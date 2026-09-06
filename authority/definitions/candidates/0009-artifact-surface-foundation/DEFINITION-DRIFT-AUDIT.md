<!-- GENERATED FILE: edit drift-audit-postimage.json and run render.py. -->

# Artifact Surface Foundation candidate drift audit

> Candidate evidence; this view is not canonical.

## Summary

- New Definition Candidates: `5`
- Live Registry Versions: `33`
- Proposed Registry Versions: `38`
- Undefined Critical Terms: `0`
- Open Artifact Type Contracts: `3`

## Findings

### ASF-DRIFT-001 (structural-gap, candidate-remediation-authored)

No canonical Artifact Type registry currently resolves admitted type versions and decision overlays.

Target: `authority/artifact-types/registry.json`

Remediation: Review the candidate Artifact Type Registry contract and initial 25-entry postimage; do not materialize it as current before admission.

### ASF-DRIFT-002 (semantic-gap, candidate-remediation-authored)

A new artifact kind that fits no admitted type has no typed fail-closed intake path.

Target: `cal.artifact-type.artifact-type-request/v1`

Remediation: Use Artifact Type Request only as candidate intake; never consume it as the proposed subject artifact.

### ASF-DRIFT-003 (package-gap, candidate-remediation-authored)

Nested package facets and independent nested package homes are not machine-declared.

Target: `cal.artifact-type.canonical-package-manifest/v1`

Remediation: Require lifecycle owner, unit of change, carrier classification, and explicit nested-package relations before migration.

### ASF-DRIFT-004 (successor-residue, open)

Capability Instance/v1 does not require canonical package-home bindings.

Target: `cal.artifact-type.capability-instance/successor`

Remediation: Preserve v1 and author a separately tested successor after the Artifact Surface Foundation is approved.

## Claim ceiling

Candidate drift evidence only. It does not change the live Definition registry, establish Artifact Type conformance, or authorize package migration.
