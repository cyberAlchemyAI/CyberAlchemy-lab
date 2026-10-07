<!-- GENERATED FILE: canonical data is admission-manifest.json. -->

# Relation Kind model — collective admission review

- Proposed decision: `CAL-DECISION-0070-RELATION-KIND-MODEL-ADMISSION`
- Relation Kinds: `23`
- Exact ordered endpoint pairs: `147`
- Typed Relations admitted: `0`
- Wildcards: `0`
- Authority effect: `none`

## Dependency gate

Decision 0069 must first admit `Relation Kind/v2` and `Typed Relation/v2`. That decision remains unapplied.

## Complete admission set

| Relation Kind | Axis | Pairs | Required qualifiers |
| --- | --- | ---: | --- |
| `relation.member-of` | `axis.membership` | 17 | `membership_role` |
| `relation.contributes-to` | `axis.contribution` | 6 | `contribution_role, contribution_scope` |
| `relation.uses-method` | `axis.method-dependency` | 6 | `usage_role` |
| `relation.evaluates` | `axis.evaluation` | 11 | `evaluation_role, evaluation_purpose` |
| `relation.realizes` | `axis.realization` | 2 | `realization_role, exact_target_version_ref` |
| `relation.engages-inquiry` | `axis.inquiry-engagement` | 4 | `inquiry_role` |
| `relation.originates-from` | `axis.origin-lineage` | 4 | `origin_role` |
| `relation.derives-from` | `axis.derivation` | 11 | `derivation_role` |
| `relation.evidence-bears-on` | `axis.evidence-polarity` | 12 | `polarity` |
| `relation.governed-by` | `axis.governance-applicability` | 5 | `governance_role` |
| `relation.declares-effect-on` | `axis.decision-effect` | 7 | `effect_kind, exact_target_version_ref` |
| `relation.instance-of` | `axis.classification` | 5 | `parent_version_ref, binding_ref` |
| `relation.binds-implementation` | `axis.implementation-binding` | 2 | `binding_role` |
| `relation.conforms-to` | `axis.conformance` | 3 | `conformance_scope, exact_version_ref, conformance_evidence_refs` |
| `relation.inherits-contract` | `axis.contract-inheritance` | 1 | `binding_ref, contract_version_ref` |
| `relation.frames` | `axis.context-framing` | 5 | `framing_role` |
| `relation.requests-resolution-of` | `axis.context-resolution-request` | 1 | `context_version_ref` |
| `relation.fulfills-request` | `axis.request-fulfillment` | 1 | `fulfillment_role` |
| `relation.successor-of` | `axis.lifecycle-succession` | 34 | `succession_effect` |
| `relation.assigned-to` | `axis.assignment` | 4 | `assignment_kind, relation_record_ref` |
| `relation.asserts-identity-of` | `axis.identity-assertion` | 3 | `assertion_kind, claim_scope` |
| `relation.scopes-authority-over` | `axis.authority-scope` | 2 | `authority_role, scope_ref` |
| `relation.carries-definition` | `axis.semantic-contract` | 1 | `definition_version_ref, definition_sha256` |

## Revised realistic example

This example is review evidence only and is explicitly excluded from the proposed admission:

```json
{
  "qualifiers": {
    "exact_target_version_ref": "experiment-design:definition-normalization-residue@1.0.0-candidate.1",
    "realization_role": "design-execution"
  },
  "relation_evidence_refs": [
    "evidence:realizes"
  ],
  "relation_kind_ref": "relation.realizes",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "experiment-run",
    "ref": "experiment-run:definition-normalization-residue:2026-10-05",
    "version_ref": "experiment-run:definition-normalization-residue:2026-10-05@example-revision-1"
  },
  "target": {
    "kind": "experiment-design",
    "ref": "experiment-design:definition-normalization-residue",
    "version_ref": "experiment-design:definition-normalization-residue@example-revision-1"
  }
}
```

The selected `relation.realizes` contract permits this exact `experiment-run → experiment-design` direction and requires exactly `realization_role` plus `exact_target_version_ref`. Reversing the endpoints, omitting either qualifier, or adding a new qualifier is rejected.

## Transaction boundary

- Admit only the exact 23 Relation Kind record bytes listed here after Decision 0069 is applied.
- Each admitted record opens only its 147 collectively enumerated exact ordered endpoint pairs; wildcards and Cartesian inference remain forbidden.
- Each Typed Relation must independently match one admitted pair and the selected Relation Kind's closed qualifier contract.
- Do not admit the 23 illustrative Typed Relation examples.
- Do not infer connections, endpoint equality, authority transfer, ontology truth, consumer activation, or runtime effect.

## Claim ceiling

This manifest binds 23 exact candidate Relation Kind records, 147 exact ordered endpoint pairs, and closed qualifier contracts. It has authority effect none and cannot admit anything before its prerequisites and a separate explicit owner decision.
