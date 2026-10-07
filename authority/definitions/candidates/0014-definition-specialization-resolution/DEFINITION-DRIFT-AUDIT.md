<!-- GENERATED FILE: edit drift-audit-postimage.json and run render.py. -->

# Definition specialization and identity resolution candidate audit

> Candidate evidence; this view is not canonical.

## Summary

- Candidate Definitions: `7`
- Predecessor Current Identities: `173`
- Predecessor Versions: `179`
- Project Identity Epoch: `retain-v1`
- Proposed Current Identities: `180`
- Proposed Versions: `186`
- Specialization Overlaps Resolved: `3`

## Findings

### STEP3-POSITIVE-DEFINITIONS (resolved-in-candidate, owner-review-open)

Five broad carrier bindings, generic Ledger, and Withdrawal Record receive exact positive Definition candidates.

Target: `CAL-DEFINITION-CANDIDATE-SPECIALIZATION-RESOLUTION-0014`

Remediation: Review and admit the exact candidate or revise it.

### STEP3-WORKFLOW-OVERLAPS (resolved-in-candidate, owner-review-open)

The three craft.* workflow meanings are declared specializations of the corresponding generic cal.* meanings, preserving both identities and active consumers.

Target: `workflow-overlap-resolution`

Remediation: Admit the resolution overlay; use generic meanings outside Craft and specialized meanings inside Craft.

### STEP3-PROJECT-IDENTITY (resolved-in-candidate, owner-review-open)

Project Identity/v1 is retained because no semantic change requires v2; admission and relation gates remain open.

Target: `cal.artifact-type.project-identity/v1`

Remediation: Resolve it through the Artifact Type effective-state registry and later owner admission.

## Claim ceiling

This candidate resolves Step 3 semantic identity and specialization choices only. It does not admit the seven Definitions, rebind or admit Artifact Types, activate workflow consumers, admit Project Identity, create a Ledger carrier, withdraw any identifier, or authorize runtime behavior.
