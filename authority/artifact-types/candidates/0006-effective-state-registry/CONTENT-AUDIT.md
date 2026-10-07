<!-- GENERATED FILE: canonical data is content-audit.json. -->

# Artifact Type content audit

- Audit: `CAL-ARTIFACT-TYPE-CONTENT-AUDIT-0001`
- Status: `candidate-audit-complete`
- Authority effect: `none`
- Descriptors audited: `56`

## Conclusion

The effective-state registry is ready for owner review. The Artifact Type set is not ready for collective content admission: current contracts have immutable-successor or evidence-refresh obligations, and several candidates require binding revisions.

## Content postures

| Posture | Count |
| --- | ---: |
| `admitted-current-content-verified` | `12` |
| `admitted-current-remediation-required` | `9` |
| `admitted-historical-preserve` | `5` |
| `candidate-content-verified-awaiting-admission` | `18` |
| `candidate-revision-required` | `5` |
| `non-effective-candidate-record` | `5` |
| `resolved-duplicate-preserve` | `2` |

## Findings

| Finding | Descriptors |
| --- | ---: |
| `admitted-semantic-successor-required` | `1` |
| `candidate-semantic-rebind-required` | `4` |
| `definition-binding-material-not-current` | `1` |
| `definition-reference-not-admitted` | `1` |
| `definition-reference-not-current` | `3` |
| `legacy-contract-sections-absent` | `14` |
| `required-semantic-field-not-schema-required` | `1` |
| `validation-evidence-not-pass` | `4` |

## Actionable descriptors

| Artifact Type | State | Content posture | Findings |
| --- | --- | --- | --- |
| `cal.artifact-type.artifact-type/v2` | `admitted-current` | `admitted-current-remediation-required` | `legacy-contract-sections-absent` |
| `cal.artifact-type.bounded-context/v2` | `admitted-current` | `admitted-current-remediation-required` | `validation-evidence-not-pass`, `legacy-contract-sections-absent` |
| `cal.artifact-type.capability-instance/v1` | `admitted-current` | `admitted-current-remediation-required` | `legacy-contract-sections-absent` |
| `cal.artifact-type.capability-realization-binding/v1` | `admitted-current` | `admitted-current-remediation-required` | `admitted-semantic-successor-required` |
| `cal.artifact-type.context-lineage-record/v1` | `admitted-current` | `admitted-current-remediation-required` | `legacy-contract-sections-absent` |
| `cal.artifact-type.context-map/v2` | `admitted-current` | `admitted-current-remediation-required` | `validation-evidence-not-pass`, `legacy-contract-sections-absent` |
| `cal.artifact-type.context-migration-manifest/v1` | `admitted-current` | `admitted-current-remediation-required` | `legacy-contract-sections-absent` |
| `cal.artifact-type.context-profile/v1` | `candidate-unadmitted` | `candidate-revision-required` | `candidate-semantic-rebind-required` |
| `cal.artifact-type.definition/v1` | `admitted-current` | `admitted-current-remediation-required` | `legacy-contract-sections-absent` |
| `cal.artifact-type.measurement-method/v1` | `candidate-unadmitted` | `candidate-revision-required` | `candidate-semantic-rebind-required` |
| `cal.artifact-type.measurement-result/v1` | `candidate-unadmitted` | `candidate-revision-required` | `candidate-semantic-rebind-required` |
| `cal.artifact-type.model-instance-binding/v1` | `candidate-unadmitted` | `candidate-revision-required` | `candidate-semantic-rebind-required` |
| `cal.artifact-type.ontology-package/v1` | `candidate-unadmitted` | `candidate-revision-required` | `definition-reference-not-admitted`, `definition-binding-material-not-current` |
| `cal.artifact-type.ubiquitous-language/v1` | `admitted-current` | `admitted-current-remediation-required` | `legacy-contract-sections-absent` |

## Relation surface

The resolved schemas expose `521` reference-shaped field paths across `56` descriptors. These fields require explicit mapping review against the candidate `23`-kind relation model. This audit does not treat that candidate model as admitted authority.

## Claim ceiling

This audit evaluates the repository-visible descriptor contracts, schemas, declared bindings, receipts, fixtures, source direction, and reference-shaped relation surfaces. It does not admit or modify an Artifact Type, prove runtime behavior, authenticate instance claims, or treat the candidate Relation Kind model as admitted authority.
