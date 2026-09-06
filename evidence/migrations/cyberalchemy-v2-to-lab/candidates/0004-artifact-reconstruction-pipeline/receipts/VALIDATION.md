<!-- GENERATED FILE: canonical data is validation.json. -->

# Artifact Reconstruction Pipeline Validation

- Result: `PASS`
- Checks: `23/23`
- Authority effect: `none`

| Check | Result | Detail |
|---|---|---|
| `approved-planning-input-current` | `PASS` | The exact selected 0003 planning decision is current and bound. |
| `d65-target-closure` | `PASS` | All six selected D65 targets plus the Evaluation dependency are represented once. |
| `approved-backlog-dependency` | `PASS` | The additional Evaluation target comes from the already selected 176-target refinement baseline. |
| `profile-result-orthogonality` | `PASS` | Evaluation results and Evaluation Profiles use distinct successor-compatible carriers. |
| `definition-schema` | `PASS` | The D65 Definition conforms to admitted Definition/v1 shape. |
| `definition-voices` | `PASS` | Scientific/formal, plain-language, and Lab domain-context voices are colocated and bounded. |
| `definition-projection` | `PASS` | The Definition human view is generated exactly from definition.json. |
| `definition-source-current` | `PASS` | The selected CAV2-D65 section bytes remain exact. |
| `definition-boundaries` | `PASS` | Carrier, binding, profile, and result meanings are explicitly non-collapsed. |
| `artifact-type-shared-validation` | `PASS` | All five Artifact Types pass the existing shared Lab validator and hostile fixtures. |
| `artifact-type-definition-bindings` | `PASS` | Every new Artifact Type has semantic Definition bindings and no authority effect. |
| `content-resolution-discriminators` | `PASS` | Every candidate Artifact Type has one unique content discriminator independent of directory placement. |
| `profile-schema-closure` | `PASS` | Both selected D65 evaluation profiles conform to the generalized Evaluation Profile/v2 candidate. |
| `profile-projection-closure` | `PASS` | Both profile human views are exact generated projections. |
| `profile-decision-separation` | `PASS` | Profiles collect all results and cannot grant product approval or post-approval authority. |
| `relation-reuse-only` | `PASS` | Exactly six selected relation identities are reused; no relation kind is minted. |
| `registry-identity-closure` | `PASS` | Eight candidate identities and proposed homes are unique and digest-bound. |
| `candidate-only-authority` | `PASS` | Every candidate authority_effect remains none. |
| `layering-complete` | `PASS` | Four evidence-gated layers expose distinct decision questions and deferrals. |
| `top-level-projections` | `PASS` | Every top-level human view is generated from canonical machine data. |
| `manifest-material-closure` | `PASS` | Every candidate material matches the immutable manifest digest. |
| `manifest-source-closure` | `PASS` | Every selected Lab and CyberAlchemy-v2 source binding is current. |
| `claim-ceiling` | `PASS` | The tested object remains a prototype construction candidate, not an admitted product or runtime. |

## Claim ceiling

PASS proves the exact L0 reconstruction vertical, its dependency closure, schemas, hostile fixtures, generated projections, and source bindings. It does not admit or install artifacts, activate a registry or runtime, execute migration, commit, push, publish, release, or deploy.
