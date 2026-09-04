<!-- GENERATED FILE: edit drift-audit-postimage.json and run render.py. -->

# Single Decision Checkpoint Definition drift audit

> Generated candidate projection; it is not canonical.

## Summary

- Candidate Definition Count: `8`
- Undefined Critical Terms Before Candidate: `8`
- Undefined Critical Terms Within Candidate: `0`
- Conflicting Current Consumer Groups: `5`
- Historical Epochs Rewritten: `0`
- Wrong Workspace Voices: `0`
- Open Definition Dependencies: `1`
- Owner Decision Required: `True`
- Downstream Governance And Migration Blockers: `4`

## Findings

### SDC-DRIFT-001 (undefined-critical-terms, resolved-in-candidate)

Authority Boundary, Decision Checkpoint, Workflow Decision Profile, User Decision Preference, Decision Bundle, Semantic Epoch, Representation Revision, and Derived Refresh are load-bearing but absent from the live registry.

Target: `authority/definitions/registry.json`

Remediation: Review the eight three-voice Definition candidates and proposed registry postimage after the Workflow dependency is resolved.

Blocking for: Canonical single-checkpoint governance and CTX08 representation-revision classification.

### SDC-DRIFT-002 (terminology-collapse, resolved-in-candidate)

Approval boundary can collapse workflow interaction placement, Governance Decision outcome, and Authority Boundary.

Target: `user-facing phrase approval boundary`

Remediation: Use Decision Checkpoint as the canonical term and retain approval boundary only as a user-facing alias.

Blocking for: Unambiguous workflow-profile and validator design.

### SDC-DRIFT-003 (definition-dependency, open)

Workflow and workflow type are load-bearing dependencies of Workflow Decision Profile but are not canonical Lab Definitions and must not be independently redefined here.

Target: `Craft Workflow definition`

Remediation: Select the exact Craft/DomainSpec Workflow definition, admit its source selector for Lab use, and create a reuse or specialization handling record before promotion review.

Blocking for: Promotion eligibility of Workflow Decision Profile and the derived governance rule.

### SDC-DRIFT-004 (semantic-version-misclassification, open)

Both CTX08 candidates declare that context meaning is preserved while classifying schema normalization as new semantic context epochs.

Target: `contexts/governance/v3 and contexts/ontology-lifecycle/v3`

Remediation: Preserve the unadmitted files as rejected candidate evidence until separately authorized replacement; author representation-revision candidates retaining the admitted v2 Semantic Epochs.

Blocking for: Correct CTX08 replacement and representation cutover.

### SDC-DRIFT-005 (lineage-misclassification, open)

The CTX08 lineage candidates describe unchanged context identity and meaning but assert semantic v2-to-v3 successor relationships.

Target: `contexts/lineage/governance/v2 and contexts/lineage/ontology-lifecycle/v2`

Remediation: Do not admit the lineage candidates. Replace their intended evidence with exact representation preimage/postimage and rollback bindings.

Blocking for: Correct CTX08 replacement; not historical v1-to-v2 lineage.

### SDC-DRIFT-006 (missing-governance-artifact-types, open)

Lab has no admitted Rule, Constitution, Workflow Decision Profile, User Decision Preference, Representation Revision, or Decision Bundle artifact types.

Target: `authority/artifact-types and authority/profiles`

Remediation: After Definition admission, author the smallest artifact-type candidates required by the invariant, Constitution rule, profile, preference, resolution evidence, and representation migration.

Blocking for: Machine-enforceable single-checkpoint governance.

### SDC-DRIFT-007 (decision-gate, open)

The live canonical registry remains byte-identical with ten admitted Definition versions; this candidate has authority_effect none.

Target: `authority/definitions/registry.json`

Remediation: Resolve the Workflow dependency, revalidate exact bytes, and present one digest-bound definition-owner decision bundle at the configured checkpoint.

Blocking for: Canonical admission of the eight candidate Definitions.

## Claim ceiling

This audit resolves eight undefined terms within a candidate and routes the Workflow dependency, governance artifact types, and CTX08 correction. It does not change the live registry, admit a Definition, adopt a rule, replace CTX08, or authorize migration.
