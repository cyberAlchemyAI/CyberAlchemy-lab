<!-- GENERATED FILE: edit drift-audit-postimage.json and run render.py. -->

# CML-07 semantic closure Definition drift audit

> Candidate evidence; this view is not canonical.

## Summary

- Predecessor Candidate Definitions: `6`
- Semantic Closure Candidate Definitions: `8`
- Composed Candidate Definitions: `14`
- Undefined Critical Terms After Candidate: `0`
- Conflicting Consumers After Successor Chain: `0`
- Open Successor Blockers: `2`

## Findings

### SC-001 (semantic-ambiguity, resolved-in-candidate)

Validation execution, schema or identity-contract conformance, implementation conformance, and runtime conformance were previously not distinguished.

Target: `CML-07 validation and conformance vocabulary`

Remediation: Use the exact Definition references and scoped conformance kinds in successor chain 0002.

### SC-002 (undefined-critical-terms, resolved-in-candidate)

Artifact Type, Evidence, Evaluation, Validation, Conformance, Validation Receipt, Identity Carrier, and Identity Lineage had no canonical Lab Definition candidates.

Target: `eight CML-07 prerequisite terms`

Remediation: Review and bind these eight candidates with candidate 0006 at the final CML-07 decision boundary.

### SC-003 (semantic-binding, resolved-in-successor-contract)

Artifact Type/v1 accepted semantic_kind labels without a semantic Definition reference.

Target: `Artifact Type registration`

Remediation: Use Artifact Type/v2 for new registrations; preserve v1 registrations through an exact predecessor reference.

### SC-004 (historical-claim-boundary, preserved)

Candidate 0006 resolved collapse only for Product, Project, Method, Craft Method, Goal, and Identity Relation, not the complete CML-07 vocabulary.

Target: `candidate 0006 CI-003`

Remediation: Keep candidate 0006 immutable and interpret its closure claim only within its named six-term scope.

### SC-005 (successor-blocker, open)

All semantic records and Artifact Type/v2 remain candidate-unadmitted.

Target: `CML07-S2`

Remediation: Include exact candidate, source, owner, registry-postimage, Artifact Type/v2, and validation digests in the configured final decision request set before S2.

### SC-006 (source-admission, open)

The three selected source ranges are current but are not admitted for the Lab semantic-closure use.

Target: `CAV2-D38 CAV2-D56 CAV2-D65 selectors`

Remediation: Author exact source-admission candidate clauses and bind them at the final CML-07 decision boundary; do not infer admission from currentness.

## Claim ceiling

This audit describes candidate semantic closure and remaining admission dependencies only. It does not change live definitions, establish conformance, admit Artifact Type/v2, or authorize CML-07 S2.
