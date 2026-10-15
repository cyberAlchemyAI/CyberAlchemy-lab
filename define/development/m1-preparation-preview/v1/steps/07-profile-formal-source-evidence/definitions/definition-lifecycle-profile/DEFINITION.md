<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Definition Lifecycle Profile

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.definition-lifecycle-profile`
- Version: `1.0.0-candidate.3`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `candidate:define-m1:profile-source-closure-unadmitted`

## Scientific/formal voice

A Definition Lifecycle Profile is a reusable, owner-qualified, version-exact contract declaring the initial posture, permitted states and directed transitions for one exact Definition version under selected governing contracts. It binds each transition to its required evaluation and review evidence, applicable owner authority, intended effect, invalidation conditions and history-preservation rules. It separates satisfied gates, recorded review, selected admission and confirmed application. Declaring the profile or satisfying a gate does not itself record a new state, select an owner Decision, apply an effect or prove that a transition occurred.

```text
P=(id,v,T,Q,q0,E,Gate,Effect,o,s,Invalidate,History); E subseteq Q x Q.
PermittedBy(P,d,a,b,I) iff ExactBinding(P,d,I) and (a,b) in E and Gate(P,d,a,b,I)=PASS.
PermittedBy(P,d,a,b,I) does not entail TransitionRecorded(d,a,b) or EffectApplied(d,Effect(P,a,b)).
ConsistentAdmittedState(d) requires applicable exact owner admission selection and confirmed application; declaration alone provides neither.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| P; id,v; T; d | Exact profile identity/revision, selected Definition representation and one exact Definition version. |
| Q; q0; E | Declared states, initial posture and finite directed transition pairs; no transition is inferred from independent state lists. |
| Gate; I | Scoped requirements and exact evidence/authority input state. PASS establishes the gate; unknown or unsupported evidence does not establish permission. |
| Effect; o; s | Declared effect, qualified authority owner and applicability scope. Effect selection and confirmed application remain separate facts. |
| Invalidate; History | Rules for changed epochs, affected evidence invalidation and immutable historical state/receipt preservation. |
| PermittedBy; TransitionRecorded; EffectApplied | Conditions allowing a transition, a separately attributable transition record and separately confirmed effect; none is silently substituted for another. |

### Boundary conditions

- The semantic meaning is independent of its carrier revision. Exact v1 bootstrap mechanics and later v2 adoption are separately declared representation/review choices.
- The declared scope is Lab Definition governance. It does not supply a general profile for unrelated artifact kinds.
- A changed subject, profile, selected source or evidence epoch invalidates affected evidence; prior material is preserved without automatic refreshing.
- Schema/projection PASS, semantic interpretation fidelity, applicable owner selection and confirmed application remain separate obligations.
- A permitted directed pair and satisfied gate do not move the subject automatically; each actual transition requires an attributable record and applicable confirmed effect.
- Initial posture is a contract declaration, not evidence of another record’s actual state.
- Pre-decision readiness is an assessment, not an extra lifecycle state. Defer/revise/reject outcomes do not silently create a withdrawal effect.

### Testable conditions

- The semantic record preserves exact identity, scope, three voices and selected carrier/generator bindings.
- Profile declarations, completed evidence, owner selection and confirmed effects have separate identifiers and evidence.
- The incident example retains the account, filters, source snapshot and saved output boundaries.
- No missing review or unperformed effect is reported as completed.

## Plain-language voice

The contract for when a Definition may change state, what evidence and authority are needed, and what history must be kept. A passed check can satisfy a condition; an actual state change still needs its declared record and applicable effect.

## Domain-context voice

Workspace: `workspace:cyberalchemy-lab`

This revised semantic binding applies to the proposed v2 profile/carrier. The candidate itself uses admitted Definition/v1 mechanics and current v1 review routes as the explicit bootstrap choice, independent of the meaning’s scope. No v2 self-approval or owner acceptance is claimed.

### Examples

- The completeness Definition stays candidate-authored while semantic review and admission remain pending.
- Even an eligible owner-reviewed Definition stays unadmitted when the admission Decision or its confirmed application is missing.

## Applicability

Shared meaning for Lab Definition lifecycle contracts, transition gates and history-preservation rules.

### Exclusions

- Profiles for unrelated artifact kinds without their own declared extension.
- Automatic owner decisions, lifecycle events, application or machine-agent permission.

## Boundaries

- The semantic meaning is independent of its carrier revision. Exact v1 bootstrap mechanics and later v2 adoption are separately declared representation/review choices.
- The declared scope is Lab Definition governance. It does not supply a general profile for unrelated artifact kinds.
- A changed subject, profile, selected source or evidence epoch invalidates affected evidence; prior material is preserved without automatic refreshing.
- Schema/projection PASS, semantic interpretation fidelity, applicable owner selection and confirmed application remain separate obligations.
- A permitted directed pair and satisfied gate do not move the subject automatically; each actual transition requires an attributable record and applicable confirmed effect.
- Initial posture is a contract declaration, not evidence of another record’s actual state.
- Pre-decision readiness is an assessment, not an extra lifecycle state. Defer/revise/reject outcomes do not silently create a withdrawal effect.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.decision@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `514f8a33054508ecd7050ddeb5241e3cd55d7ccf7bfd8677323ebea6318627be` | `admitted` |
| cal.definition.artifact-type@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `90c61c2fa5a5f1d5d0a96d8e6c1f4b1f902e8ad57d85ef1e315e549470abb69f` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /transitions | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /separation_invariants | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| cal.definition.admission-transaction@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `af1468a3eaec84c1146a1b570f4154738d586d9691f846fbf56f9fa5228c3b86` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /states | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /initial_state | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /subject_artifact_type_ref | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /owner_ref | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| CAL-OWNERS-FOUNDATION-01 | /role_assignments/2 | `bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d` | `admitted` |
| CAL-OWNERS-FOUNDATION-01 | /role_assignments/4 | `bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d` | `admitted` |

## Primary consumers

- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/staged-carriers/definition-lifecycle-profile/artifact.json

## Lookup and drift

- Index: `define/development/m1-preparation-preview/v1/DEFINITIONS-INDEX.md` / `cal.definition.definition-lifecycle-profile`
- Drift owner: `role:definition-owner`
- Audit: `define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/source-closure.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

No typed relations declared.

## Evidence

- define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/semantic-binding-review.json
- define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/compatibility.json
- define/development/m1-preparation-preview/v1/steps/06-profile-definition-meaning-review/interpretation.json
- define/development/m1-preparation-preview/v1/steps/06-profile-definition-meaning-review/example.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/formal-core.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/formal-results.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/correspondence.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/source-closure.json

## Residue

- owner-interpretation-and-semantic-fidelity-decision-pending
- bounded-model-not-whole-natural-language-consistency
- exact-registry-index-review-postimages-pending
- carrier-profile-adoption-pending
- owner-admission-pending

## Claim ceiling

Source-completed candidate with unchanged candidate.2 normative statement and formal expression. Finite model/exhaustive rule evidence applies only to the explicit interpreted core and pinned inputs. It does not establish whole-repository consistency, real-world owner authentication, semantic fidelity acceptance, admission or applied effects.
