<!-- GENERATED FILE: edit the bound canonical profile JSON. -->

# Definition/v2 evaluation profile

> Generated from `evaluation.json`; this view is not canonical.

- Record: `CAL-EVALUATION-DEFINITION-V2`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Owner: `role:evidence-conformance-owner`
- Subject: `cal.artifact-type.definition/v2`
- Profile schema SHA256: `533d6487edd40a3006e9deb73c205ad9ae0f87562f665d9d995ca8cdc5d72d16`
- Check/phase contract: `define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles/check-contracts.json`
- Check/phase contract SHA256: `bedd3309bd4c1c6c079cddcc05a113159f5868c60f432003543062b986c998c7`

## Outcomes

- `PASS`
- `FAIL`
- `NOT_EVALUABLE`

## Checks

| Check | Purpose | Blocking prerequisites |
| --- | --- | --- |
| DEF2-01-REPRESENTATION | Resolve exact subject type, schema and representation; reject unknown fields and changed digests. | None |
| DEF2-02-VOICES | Require three present voices with explanatory voices explicitly non-normative. | DEF2-01-REPRESENTATION |
| DEF2-03-SOURCES | Resolve each exact source, selector, integrity, standing at capture and permitted target use. | DEF2-01-REPRESENTATION |
| DEF2-04-OWNER | Resolve semantic/drift roles and admitted assignments within the exact scope. | DEF2-01-REPRESENTATION |
| DEF2-05-PROJECTION | Bind exact generator and require canonical JSON to match deterministic human projection. | DEF2-01-REPRESENTATION |
| DEF2-06-CONNECTIONS | Close declared dependency and relation obligations, endpoint pairs and carrier roles. | DEF2-01-REPRESENTATION |
| DEF2-07-REGISTRY-DRIFT | Verify exact proposed registry, unique index entry, generated lookup and accountable drift route. | DEF2-01-REPRESENTATION |
| DEF2-08-IMPACT | Resolve named consumers, compatibility, source/use gaps and all required current affected bindings. | DEF2-03-SOURCES, DEF2-06-CONNECTIONS |
| DEF2-09-SEMANTIC-ASSURANCE | Inspect scoped non-collapse and internal-consistency evidence with exact interpretation and coverage. | DEF2-02-VOICES, DEF2-03-SOURCES |
| DEF2-10-FIDELITY | Record attributable interpretation/voice/source fidelity review of the exact meaning. | DEF2-08-IMPACT, DEF2-09-SEMANTIC-ASSURANCE |
| DEF2-11-PROFILE-COMPATIBILITY | Resolve applicable profile/carrier standing, exact bindings and foundational compatibility. | DEF2-01-REPRESENTATION |
| DEF2-12-REVIEW-COHORT | Freeze exact reviewed inputs, requested effects, owner routes and deterministic output recipes. | DEF2-07-REGISTRY-DRIFT, DEF2-08-IMPACT, DEF2-10-FIDELITY, DEF2-11-PROFILE-COMPATIBILITY |
| DEF2-13-ADMISSION-DECISION | Verify the separate exact owner decision selecting this admission effect. | DEF2-12-REVIEW-COHORT |
| DEF2-14-APPLICATION | Verify the separate exact admission application and effective lookup visibility. | DEF2-13-ADMISSION-DECISION |

## Admission rule

All checks 01-12 PASS on current exact inputs; check 13 is NOT_EVALUABLE solely because owner admission has not been selected; check 14 is excluded before application. If a Decision already exists, assess its binding and application through the later phases rather than treating it as pending. Required phase/check scopes and exact inputs are in the bound check contract. Eligibility is not a lifecycle state or authority grant. Final admission and application are separate checks.

## Claim ceiling

Proposed Definition/v2 evaluation profile and explicit profile-carrier successor. No automatic owner review, semantic truth, profile adoption, Definition admission, current lookup change or runtime implementation.
