<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Definition Evaluation Profile

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.definition-evaluation-profile`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `candidate:define-m1-profile-carrier-compatibility:authored`

## Scientific/formal voice

A Definition Evaluation Profile is a reusable, owner-qualified, version-exact contract for evaluating a declared Definition representation and its review package. It specifies the subject kind, exact input and governing-contract selection, required checks, evidence requirements, outcomes, causal blockers, phase-specific aggregation, pre-decision eligibility and claim limits. It prescribes how an Evaluation is assessed; it is not an Evaluation execution or result. It does not select owner admission, apply an effect or change a Definition lifecycle state.

```text
EP=(id,revision,subject,selection,checks,outcomes,blockers,phases,aggregation,owner,scope,ceiling); Evaluation(S,I,EP) produces scoped evidence O. Declaration(EP) does not entail Executed(Evaluation), Admitted(S), or Applied(S).
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

The rulebook for checking one exact Definition and its review package. It states what evidence is needed and what each outcome means. Applying it produces evidence; the owner still selects admission separately.

## Domain-context voice

Workspace: `workspace:cyberalchemy-lab`

This scoped meaning supplies the missing semantic binding for the proposed v2 profile carrier. It is authored using existing admitted v1 Definition mechanics so the new profile does not have to approve its own meaning. Both semantic owner review and admission remain pending.

### Examples

- The v2 candidate lists 14 checks and excludes admission selection/application from pre-decision validation.
- The export completeness record can pass representation while semantic fidelity remains not evaluable.

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
| cal.definition.evaluation@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `7ca1fc6de116223f93d026856c7780320d600b79e454c0b4ef957bd03dd24a7b` | `admitted` |
| cal.definition.definition@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.artifact-type@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `90c61c2fa5a5f1d5d0a96d8e6c1f4b1f902e8ad57d85ef1e315e549470abb69f` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | / | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |

## Primary consumers

- define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/carriers/definition-evaluation-profile/artifact.json
- define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles/evaluation.json

## Lookup and drift

- Index: `define/development/m1-preparation-preview/v1/DEFINITIONS-INDEX.md` / `cal.definition.definition-evaluation-profile`
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
