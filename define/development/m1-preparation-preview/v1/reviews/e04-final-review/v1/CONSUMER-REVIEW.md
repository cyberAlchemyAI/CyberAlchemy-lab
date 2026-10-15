# Exact consumer preservation and update review

This current review overlay classifies all 37 selected Definition records: 34 direct source users, two evidence-only users and the foundational predecessor subject. It proposes no changes to those records. Exact paths, hashes, premises and limits are in the [machine preview](consumer-review-preview.json).

| Term | Exact version | Reference class | Proposed disposition |
| --- | --- | --- | --- |
| Craft Method | `CAV2-D20@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Method | `CAV2-D32@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Goal | `CAV2-D59@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Project | `CAV2-D60@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Workflow | `DS-D1.9@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Artifact Surface Classification | `cal.definition.artifact-surface-classification@1.0.0-candidate.2` | direct source | Preserve exact record and historical binding; no implicit migration |
| Artifact Type | `cal.definition.artifact-type@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Artifact Type Registry | `cal.definition.artifact-type-registry@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Artifact Type Request | `cal.definition.artifact-type-request@1.0.0-candidate.2` | direct source | Preserve exact record and historical binding; no implicit migration |
| Artifact Type Resolution | `cal.definition.artifact-type-resolution@1.0.0-candidate.2` | direct source | Preserve exact record and historical binding; no implicit migration |
| Authority Boundary | `cal.definition.authority-boundary@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Bounded Context | `cal.definition.bounded-context@2.0.0-candidate.1` | evidence only | Preserve exact record and historical binding; no implicit migration |
| Canonical Package Home | `cal.definition.canonical-package-home@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Canonical Package Manifest | `cal.definition.canonical-package-manifest@1.0.0-candidate.2` | direct source | Preserve exact record and historical binding; no implicit migration |
| Conformance | `cal.definition.conformance@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Context Map | `cal.definition.context-map@2.0.0-candidate.1` | evidence only | Preserve exact record and historical binding; no implicit migration |
| Decision Checkpoint | `cal.definition.decision-checkpoint@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Definition | `cal.definition.definition@1.0.0-candidate.1` | foundational subject self-reference | Preserve exact record and historical binding; no implicit migration |
| Derived Refresh | `cal.definition.derived-refresh@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Evaluation | `cal.definition.evaluation@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Evidence | `cal.definition.evidence@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Identity Carrier | `cal.definition.identity-carrier@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Identity Lineage | `cal.definition.identity-lineage@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Identity Relation | `cal.definition.identity-relation@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Product | `cal.definition.product@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Repository Migration Manifest | `cal.definition.repository-migration-manifest@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Representation Revision | `cal.definition.representation-revision@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Semantic Epoch | `cal.definition.semantic-epoch@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Typed Connection Extension Rule | `cal.definition.typed-connection-extension-rule@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| User Decision Preference | `cal.definition.user-decision-preference@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Validation | `cal.definition.validation@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Validation Receipt | `cal.definition.validation-receipt@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Workflow Decision Profile | `cal.definition.workflow-decision-profile@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Decision Checkpoint | `craft.definition.decision-checkpoint@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Decision Request Set | `craft.definition.decision-request-set@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| User Decision Preference | `craft.definition.user-decision-preference@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |
| Workflow Decision Profile | `craft.definition.workflow-decision-profile@1.0.0-candidate.1` | direct source | Preserve exact record and historical binding; no implicit migration |

## Type contracts

| Contract | Disposition |
| --- | --- |
| `cal.artifact-type.definition/v2` | explicit descriptor binding successor proposed |
| `cal.artifact-type.evaluation-profile/v1` | preserve exact v1 contract as historical-version-compatible bootstrap; future v2 adoption does not rewrite old profile subjects |
| `cal.artifact-type.lifecycle-profile/v1` | preserve exact v1 contract as historical-version-compatible bootstrap; future v2 adoption does not rewrite old profile subjects |

## Operational and narrative witnesses

These source observations are not runtime execution or new M1 qualification. The documentation change captured since step 5 predates this review; its current captured bytes are preserved here.

| Selected file | Proposed disposition |
| --- | --- |
| `implementation/define-cli/v1/src/lab-cli.mjs` | preserve current runtime and exact source/envelope epochs; stale context must be regenerated by future authorized work, no private-store rebase |
| `implementation/lab-review/candidates/v1/review.py` | preserve specialized C10 scope; generic Define review uses separately declared v2 preparation interfaces, no automatic C10 role substitution |
| `docs/lab/how-to/prepare-definition.md` | existing exact-carrier/three-voice/owner explanations are compatible; latest candidate review queue supplies current proposed routes |
| `define/INTEGRATION.md` | Point readers to the current preparation review and retain the distinction when future M1 runtime documentation is updated. |
| `implementation/define-cli/v1/CONTRACT.md` | Point readers to the current preparation review and retain the distinction when future M1 runtime documentation is updated. |

## Historical connections

Preserve the exact predecessor’s embedded references and admission history. Do not transfer its Definition-to-Role governed-by reference under the Definition-to-Constitution contract. Do not turn a Source Admission reference into a Source node. Explicit semantic owner fields and source-admission provenance remain separate. No new global Typed Relations are created.

## Remaining scope

This is a pending review of scoped preservation and future update conditions. Unknown/private/external consumers, new source rebindings, actual runtime integration and independent owner/application effects remain outside its evidence claim.
