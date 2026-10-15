# Step 4 — Definition/v2 evaluation and lifecycle profiles

Both profiles and their explicit carrier/schema/renderer successors are **prepared candidates**. No profile or Definition is admitted, and no lifecycle state has changed.

## What each profile does

- **Evaluation:** which exact checks apply, what evidence establishes each result, and which checks determine representation, validation, review readiness, selected admission or confirmed application.
- **Lifecycle:** what must happen before one exact Definition moves between authored, validated, reviewed, admitted, superseded and withdrawn states.

## Evaluation checks

| Check | Question |
| --- | --- |
| 01 Representation | Does the exact JSON meet its applicable carrier/schema? |
| 02 Voices | Are all three required voices structurally present and marked correctly? |
| 03 Sources | Are exact sources admitted/current for the declared use? |
| 04 Owner | Is the owner assignment applicable to this exact scope? |
| 05 Projection | Does the bound generator reproduce the human view? |
| 06 Connections | Are declared required couplings and endpoint contracts closed? |
| 07 Registry and drift | Are proposed lookup/index/audit material and routes exact? |
| 08 Impact | Are affected consumers and required compatibility obligations resolved? |
| 09 Semantic assurance | Is scoped non-collapse/internal-consistency evidence adequate? |
| 10 Fidelity | Has the owner reviewed the exact interpretation and aligned meanings? |
| 11 Profile compatibility | Are the applicable profiles/carriers and foundational bindings adopted and compatible? |
| 12 Review cohort | Are exact subjects, evidence, requested effects and recipes frozen? |
| 13 Admission selection | Did the owner select this exact admission effect? |
| 14 Application | Was that exact authorized effect applied and made coherently visible? |

Results are PASS, FAIL or NOT_EVALUABLE. Missing evidence is NOT_EVALUABLE; established violation is FAIL. Independent checks continue even when others cannot run.

**Before the admission decision:** checks 01–12 must pass; check 13 may be pending solely because the owner has not selected admission; check 14 is excluded. Therefore the future decision is not a prerequisite for becoming ready to request that decision.

Representation uses checks 01/02/05. Validation uses 01–09 and 11. Owner-reviewed requires 01–12 plus the applicable exact owner review record. Evidence alone performs no transition.

## The identifier-completeness Definition today

The selected example is the exact existing repository candidate from step 3, preserved unchanged.

| Group | Present result | Why |
| --- | --- | --- |
| Representation and voices | PASS for bounded executed structural checks | Closed Definition/v2 schema, three voice structures and exact schema binding. |
| Human projection | PASS for bounded executed projection checks | Two renders match the saved generated view. |
| Sources and owner applicability | NOT_EVALUABLE as full profile checks | Foundational structural source and owner role exist; complete domain/use applicability evidence is pending. |
| Connections, registry, drift and consumers | NOT_EVALUABLE | Proposed/illustrative references and required coupling/impact closure remain unresolved. |
| Semantic assurance and fidelity | NOT_EVALUABLE | Formal coverage and exact owner fidelity acceptance are pending. |
| Profile compatibility and frozen review cohort | NOT_EVALUABLE | These schemas/profiles remain candidates and the full admission cohort is not closed. |
| Owner admission and application | Not selected / not performed | They remain separate later phases. |

Current lifecycle: **candidate-authored**. The example is not ready for admission. The current table is a bounded preview assessment, not a full adopted-profile evaluator result.

## How it would progress

```text
candidate-authored
    | applicable adopted profiles + full validation evidence + recorded transition
validated-candidate
    | exact owner fidelity/review + closed review cohort + recorded transition
owner-reviewed
    | exact owner admission Decision + confirmed authorized application
admitted
    | later exact successor or withdrawal effect + confirmed application
superseded / withdrawn
```

Readiness is an assessment, not an added lifecycle state. A review can inspect gaps while a candidate remains authored. An actual owner-reviewed state requires the declared completed gate. Changed bytes or selected standing create a new epoch and invalidate affected evidence; historical receipts are preserved.

## The incident has its own result

For Northstar, status=active, S-1042 and E-1042, the illustrative 12,000 required identifiers and 11,800 matched identifiers imply 200 missing. The proposed `CompleteIds` criterion would be false. That does not mean the Definition representation failed. Conversely, a structurally valid or admitted Definition does not make an export complete, establish its observed cause, permit extraction/repair or close the incident.

## Explicit mechanics amendment

The admitted predecessor profile schema hard-codes Definition/v1, and its renderer prints v1 headings. The proposed closed v2 profile carriers bind Definition/v2, exact schema and check-contract digests, and a separate versioned renderer. Existing v1 bytes remain preserved. The new profile types need their own full Artifact Type/schema evolution and adoption closure before enforcement.

## Complete review materials

- [Evaluation profile](EVALUATION.md) / [machine record](evaluation.json)
- [Lifecycle profile](LIFECYCLE.md) / [machine record](lifecycle.json)
- [Exact check and phase contracts](check-contracts.json)
- [Schema/mechanics amendment](carrier-amendment.json)
- [Closed proposed profile schemas](profile-carriers.schema.json)
- [Operational interpretation](interpretation.json)
- [Example walkthrough](example-walkthrough.json)
- [Independent review targets](review-targets.json)
- [Frozen profile bundle](profile-bundle.json)
- [Preparation checks](review-checks.json)
- [Progress](../../progress.json)

Next: complete profile Artifact Type/compatibility and foundational consumer/connection dispositions, then exact source and formal/fidelity closure. The working M1 preparation implementation remains pending.
