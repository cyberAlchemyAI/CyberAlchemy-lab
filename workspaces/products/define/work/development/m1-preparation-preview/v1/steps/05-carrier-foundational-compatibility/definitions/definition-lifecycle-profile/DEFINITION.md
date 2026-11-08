<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Definition Lifecycle Profile

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.definition-lifecycle-profile`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `candidate:define-m1-profile-carrier-compatibility:authored`

## Scientific/formal voice

A Definition Lifecycle Profile is a reusable, owner-qualified, version-exact contract declaring the lifecycle states, initial posture, permitted ordered transitions, required evidence and owner authority, transition effects, invalidation and history-preservation rules for a declared Definition representation. It separates validation, review, admission selection and confirmed application. It specifies conditions for a transition; it is not the current state of a Definition, a transition event, an owner Decision or proof that an effect occurred.

```text
LP=(id,revision,subject,states,initial,transitions,gates,effects,owner,scope,invalidation,history); GateSatisfied(d,from,to,LP) does not entail TransitionApplied(d,from,to). AdmissionEffective(d) requires applicable owner selection and confirmed application.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| EP / LP | One exact profile contract with explicit subject, scope, owner and evidence/authority ceiling. |
| S / d; I; O | An exact Definition subject, selected input state and scoped evaluation evidence. |
| GateSatisfied; TransitionApplied | Evidence satisfying declared conditions and separately confirmed actual transition/application. |

### Boundary conditions

- Profile contract, exact subject, Evaluation result, owner Decision and confirmed application remain distinct.
- Changed check semantics, subject scope or transition effects require an explicit successor and schema/consumer compatibility disposition.
- Outcome aggregation is phase-specific; future admission/application cannot be prerequisites for pre-decision eligibility.
- Historical v1 governance records preserve their scope and exact standing; they do not adopt the new v2 profile by citation.

### Testable conditions

- The exact semantic record conforms to admitted Definition/v1 and its bound generator.
- The profile declares exact subject/input selection, owner and claim limits.
- Examples distinguish declared rules, missing evidence, selected owner decisions and confirmed effects.
- A changed profile or subject epoch cannot silently refresh historical evidence.

## Plain-language voice

The rulebook for when one exact Definition may change state and what that change means. A rulebook or a passed check does not move the record by itself; the declared authority, evidence and application must be present.

## Domain-context voice

Workspace: `workspace:cyberalchemy-lab`

This scoped meaning supplies the missing semantic binding for the proposed v2 profile carrier. It is authored using existing admitted v1 Definition mechanics so the new profile does not have to approve its own meaning. Both semantic owner review and admission remain pending.

### Examples

- The v2 candidate preserves authored, validated, reviewed, admitted, superseded and withdrawn states.
- The completeness example remains authored until its actual required gates and transitions are completed.

## Applicability

Lab Definition evaluation/lifecycle contracts and their explicit versioned carriers. The bootstrap carrier is exact admitted Definition/v1 under the current foundational Definition and v1 review profiles.

### Exclusions

- Profiles for unrelated artifact kinds without their own declared extension.
- Automatic owner decisions, lifecycle events, application or machine-agent permission.

## Boundaries

- Profile contract, exact subject, Evaluation result, owner Decision and confirmed application remain distinct.
- Changed check semantics, subject scope or transition effects require an explicit successor and schema/consumer compatibility disposition.
- Outcome aggregation is phase-specific; future admission/application cannot be prerequisites for pre-decision eligibility.
- Historical v1 governance records preserve their scope and exact standing; they do not adopt the new v2 profile by citation.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.decision@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `514f8a33054508ecd7050ddeb5241e3cd55d7ccf7bfd8677323ebea6318627be` | `admitted` |
| cal.definition.artifact-type@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `90c61c2fa5a5f1d5d0a96d8e6c1f4b1f902e8ad57d85ef1e315e549470abb69f` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | / | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |

## Primary consumers

- define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/carriers/definition-lifecycle-profile/artifact.json
- define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles/lifecycle.json

## Lookup and drift

- Index: `define/development/m1-preparation-preview/v1/DEFINITIONS-INDEX.md` / `cal.definition.definition-lifecycle-profile`
- Drift owner: `role:definition-owner`
- Audit: `define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/obligations.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

No typed relations declared.

## Evidence

- define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/semantic-binding-review.json
- define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/compatibility.json

## Residue

- exact-owner-meaning-and-fidelity-review-pending
- v1-definition-review-postimages-pending
- bounded-semantic-assurance-pending
- exact-owner-admission-pending

## Claim ceiling

New scoped Definition/v1 semantic candidate for profile-carrier registration. Exact v1 carrier/profile compatibility is explicit. No new admitted term, self-approval, source-use expansion, global relation, transition or runtime effect.
