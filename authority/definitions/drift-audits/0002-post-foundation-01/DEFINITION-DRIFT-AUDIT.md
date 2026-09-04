<!-- GENERATED FILE: edit the bound JSON source and rerun render.py. -->

# Definition drift audit

> Generated from `drift-audit.json`; this view is not canonical.

- Status: `candidate-unadmitted`
- Authority effect: `none`
- Owner: `role:evidence-conformance-owner`

## Summary

- Undefined Critical Terms: `1`
- Conflicting Consumers: `0`
- Stale Entries: `0`
- Wrong Workspace Voices: `0`

## Findings

### CAL-DRIFT-001-UNDEFINED-DEFINITION (blocker)

The critical term Definition still has no admitted Definition instance in the empty canonical registry. A revised Definition/v1 artifact-type candidate does not satisfy this semantic gap.

Target: `authority/definitions/registry.json`

Remediation: After the revised Definition/v1 artifact type is separately admitted, author one Definition/v1 instance candidate for Definition with all three voices and prepare synchronized registry, index, and drift-audit postimages for a separate promotion decision.

### CAL-DRIFT-002-SOURCES-ADMITTED (info)

The exact CAV2-D21, CAV2-D33, and CAV2-D51 selector digests are admitted for their individually bounded Foundation-01 target uses by CAL-DECISION-0013-FOUNDATION-01-ADMISSION.

Target: `docs/decisions/0013-foundation-01-admission/decision.json`

Remediation: Bind each use to the matching selector digest and source-admission record; do not infer admission of the full legacy file, legacy status, or broader meaning.

### CAL-DRIFT-003-NO-CONFLICTING-CONSUMER (info)

No admitted Definition instance or canonical Definition consumer exists, so conflicting canonical consumer wording is not currently observable.

Target: `authority/artifact-types/definition/v1/candidates/0002-post-foundation-01/artifact.json`

Remediation: Rerun this audit when Definition/v1 is admitted, a Definition instance is proposed, or a semantic consumer is added.

## Claim ceiling

This is the refreshed post-Foundation-01 candidate drift snapshot. It resolves only the obsolete sources-pending finding and preserves the undefined-Definition blocker. It does not admit Definition/v1, create or promote a Definition, change the empty registry, establish semantic truth, or authorize implementation, publication, or deployment.
