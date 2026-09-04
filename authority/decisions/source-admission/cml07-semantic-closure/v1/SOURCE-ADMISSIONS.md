# CML-07 Semantic Closure Source Admissions

> Generated from `admissions.json`. Do not edit this projection directly.

- Record: `CAL-SOURCE-ADMISSIONS-CML07-SEMANTIC-CLOSURE-V1`
- Status: `candidate-unadmitted`
- Authority effect: `none-until-bound-decision`
- Owner: `role:source-admission-owner` (`person:<vrondelli>`)
- Construction unit: `CML07-W0B-SEMANTIC-CLOSURE-REVIEW`

## Exact selections

### CAL-SOURCE-ADMISSION-CML07-CAV2-D38

- Source: `domainspec-core:cyberAlchemy-v2/authority/definitions/DEFINITIONS.md:2509-2571`
- Selected SHA-256: `8472c2f6b75902c8ce2a81ae1b3980657662d2b519571a948e43580f79889fb5`
- Target Definitions: `cal.definition.evidence`, `cal.definition.evaluation`, `cal.definition.conformance`, `cal.definition.validation-receipt`
- Permitted use: Evidence, Evaluation, scoped Conformance, and non-authoritative Validation Receipt semantics.
- Non-effects:
  - Does not admit CAV2-D38 or any derived Lab Definition.
  - Does not make validation imply conformance.
  - Does not grant authority through a receipt.

### CAL-SOURCE-ADMISSION-CML07-CAV2-D56

- Source: `domainspec-core:cyberAlchemy-v2/authority/definitions/DEFINITIONS.md:4116-4223`
- Selected SHA-256: `b675ec6ad0949edb8d8527ec3f352422889916f39aa74825269b7f81487f14ed`
- Target Definitions: `cal.definition.artifact-type`, `cal.definition.validation`, `cal.definition.conformance`
- Permitted use: Artifact Type construction, explicit validation criteria, and profile-scoped conformance semantics.
- Non-effects:
  - Does not admit CAV2-D56 or any derived Lab Definition.
  - Does not activate Artifact Type/v2.
  - Does not establish implementation or runtime conformance.

### CAL-SOURCE-ADMISSION-CML07-CAV2-D65

- Source: `domainspec-core:cyberAlchemy-v2/authority/definitions/DEFINITIONS.md:5092-5290`
- Selected SHA-256: `20ae1c5687973def6eb0b2cce1a96d44d8ecb45b64dd42fd461293dfe2b0bfdd`
- Target Definitions: `cal.definition.evidence`, `cal.definition.conformance`
- Permitted use: Construction-invariant evidence ordering and the separation of conformance from predecessor admission.
- Non-effects:
  - Does not admit CAV2-D65 or any derived Lab Definition.
  - Does not satisfy any construction predecessor by declaration.
  - Does not authorize S2 construction.

## Claim ceiling

This candidate selects three exact legacy byte ranges for CML-07 semantic closure only. It does not admit a source, Definition, Artifact Type, owner, identity carrier, conformance claim, implementation, publication, deployment, or stable release.
