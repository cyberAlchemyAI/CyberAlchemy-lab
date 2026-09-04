<!-- GENERATED FILE: edit the bound JSON source and rerun render.py. -->

# Artifact Type v1

> Generated from `artifact.json`; this view is not canonical.

- Status: `candidate-unadmitted`
- Authority effect: `none`
- Owner: `role:artifact-type-owner`

## Bounded self-application

Artifact Type/v1 validates only its own closed representation and the explicitly listed registered type bindings. It cannot create new semantic kinds, owners, lifecycle meanings, or admission authority.

Bootstrap gate: One immutable human admission decision must bind Artifact Type/v1, the Foundation-01 manifest, owner assignments, profiles, source admissions, registry, drift audit, projections, and validation receipt as one cohort.

## Registered artifact types

| Type | Semantic kind | Schema | Purpose |
| --- | --- | --- | --- |
| `cal.artifact-type.artifact-type/v1` | `artifact-type` | `authority/artifact-types/artifact-type/v1/schema.json` | Defines and validates bounded artifact-type contracts, including its own bootstrap root. |
| `cal.artifact-type.definition/v1` | `definition` | `authority/artifact-types/definition/v1/schema.json` | Validates stable scoped term meaning with three colocated voices and drift routing. |
| `cal.artifact-type.lifecycle-profile/v1` | `lifecycle-profile` | `authority/foundation/v1/schema.json` | Defines lifecycle vocabulary and transitions without embedding lifecycle state in semantic artifacts. |
| `cal.artifact-type.evaluation-profile/v1` | `evaluation-profile` | `authority/foundation/v1/schema.json` | Defines collect-all checks and result semantics without granting admission. |
| `cal.artifact-type.owner-registry/v1` | `owner-registry` | `authority/foundation/v1/schema.json` | Binds stable principals to separately scoped roles without collapsing their decisions. |
| `cal.artifact-type.source-admission/v1` | `source-admission` | `authority/foundation/v1/schema.json` | Binds exact external selector bytes and a bounded admission effect. |
| `cal.artifact-type.definition-registry/v1` | `definition-registry` | `authority/foundation/v1/schema.json` | Owns the exact admitted Definition set while generating lookup views. |
| `cal.artifact-type.drift-audit/v1` | `drift-audit` | `authority/foundation/v1/schema.json` | Records conflicting wording, undefined terms, stale refs, missing voices, and remediation routes. |
| `cal.artifact-type.foundation-manifest/v1` | `foundation-manifest` | `authority/foundation/v1/schema.json` | Binds one immutable admission cohort and its D65 claim ceiling. |

## Claim ceiling

Artifact Type/v1 is a self-validating bootstrap candidate. Neither self-description, type registration, schema PASS, nor placement admits it or any registered type. Admission requires the exact future human decision named by the Foundation-01 manifest.
