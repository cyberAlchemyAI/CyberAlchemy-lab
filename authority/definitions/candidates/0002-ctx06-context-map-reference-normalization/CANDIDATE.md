<!-- GENERATED FILE: edit candidate.json and run render.py. -->

# CTX06 Context Map reference normalization candidate

> Generated from the machine-canonical candidate manifest; it has no authority effect.

- Candidate: `CAL-DEFINITION-CANDIDATE-SET-CTX06-REFERENCE-NORMALIZATION-0002`
- Status: `candidate-authored-awaiting-validation-and-owner-review`
- Authority effect: `none`

## Bound successor Definitions

| ID | Version | Predecessor | Path | Digest |
| --- | --- | --- | --- | --- |
| `cal.definition.bounded-context` | `2.0.0-candidate.1` | `cal.definition.bounded-context@1.0.0-candidate.1` | `authority/definitions/candidates/0002-ctx06-context-map-reference-normalization/definitions/bounded-context/v2/definition.json` | `6ee155d2e7427e33357e55e56bc5228c2b584ea435bb9dc516ddb66385f590c0` |
| `cal.definition.context-map` | `2.0.0-candidate.1` | `cal.definition.context-map@1.0.0-candidate.1` | `authority/definitions/candidates/0002-ctx06-context-map-reference-normalization/definitions/context-map/v2/definition.json` | `677ff95db15b30a80e2d59673286142337c3a513e52fd27dd033fe710f8de050` |

## Normalization

Context Maps solely own exact endpoint membership and directional cross-context relationships. Bounded Context records do not canonically backreference maps. Reverse membership is generated from canonical Context Maps and is not a second authority.

## Evaluation posture

Collect all structural, semantic-ownership, admitted-source, exact-byte, projection, registry-postimage, drift, and hostile-fixture checks. The owner decision remains NOT_EVALUABLE during candidate validation.

## Remaining gate

An exact definition-owner decision bound to both successor Definition digests and the complete registry/drift postimages is required before either version becomes canonical.

## Claim ceiling

This package is a two-Definition normalization candidate with proposed registry and drift postimages. PASS does not admit either Definition, change the live registry, revise artifact types, contexts, maps, migrations, implementation, publication, deployment, or stable-release state.
