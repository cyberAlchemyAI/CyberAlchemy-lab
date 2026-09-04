<!-- GENERATED FILE: edit drift-audit-postimage.json and run render.py. -->

# Canonical Package Home candidate drift audit

> Candidate evidence; this view is not canonical.

## Summary

- Findings: `3`
- Blocking: `2`
- Resolved By Candidate: `1`

## Findings

### CPH-DRIFT-01 (semantic, resolved-by-candidate)

Existing definitions distinguish identities and say capability instances remain with their owning module, but no named rule selects one canonical package home from lifecycle ownership and unit of change.

Target: `cal.definition.canonical-package-home@1.0.0-candidate.1`

Remediation: Review the candidate as the missing composition rule; do not reinterpret orthogonality as one physical root per semantic axis.

### CPH-DRIFT-02 (admission, open)

The selected CAV2 definition bytes are current but not admitted for this specific Lab Definition use.

Target: `candidate.json#source_bindings`

Remediation: At the single configured decision boundary, admit or reject the exact source selections separately from Definition admission.

### CPH-DRIFT-03 (enforcement, open)

The admitted Capability Instance Artifact Type does not yet require canonical_package_home_ref, lifecycle_owner_ref, or unit_of_change_ref.

Target: `cal.artifact-type.capability-instance/successor`

Remediation: After semantic selection, author a successor Artifact Type and migration candidate that bind this Definition without rewriting the admitted v1 contract.

## Claim ceiling

This audit identifies one semantic clarification and two open successor obligations. It does not admit sources, Definitions, Artifact Types, or a migration.
