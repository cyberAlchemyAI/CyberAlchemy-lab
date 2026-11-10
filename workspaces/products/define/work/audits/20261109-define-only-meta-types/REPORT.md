# Define-only AlchLang meta-type audit

Result: mostly appropriate resource kinds, but the proposal is not yet meta-type-complete or compile-ready. One source/profile syntax failure is reproduced, and five responsibility/profile/storage obligations need correction or explicit completion. No runtime or canonical semantics were changed.

Scope: the seven Define-only design extensions, all 13 active backend meta-types, the additional Entry boundary and the current profiles/implementation on which the proposal relies. This is not a requirement to insert every meta-type into every module. UI candidate/deferred types and superseded Saga are not applicable.

## Actual checks

- Actual selected toolchain: AlchLang 0.7.0-candidate.0 and Craft Core 1.3.0.
- Original generic frontend: 6 of 7 design code blocks parse. D03 fails at the pendingAnswer Policy case label on the pure-profile source path.
- A private harness with explicit PreparationFacts and simple case labels generates through the original checked compiler. All 6 Policy decision cases pass.
- A separate private guard Operation harness, using unchanged shared type bodies plus an explicitly recorded Rule root, generates and passes 4 shape cases. This proves zero-effect guard Operations are allowed in this dialect; it does not prove real source/membership/permission validation.
- Current migration evidence revalidation passes: 341 retained checks, 44 selected bindings, current source/retirement proof. Those 341 tests were not all rerun here.
- Full proposed service compilation, profile wiring, authenticated execution and end-to-end tests were not performed. These isolated probes do not implement the design.

## Findings

### MT-01 (P1): confirmed selected-profile syntax failure

Target: `DESIGN.md D03 / NextSemanticAction`.

Six of seven proposed blocks pass original generic frontend parsing. D03 rejects pendingAnswer as a Policy step-name. A five-field PreparationFacts contract is also not declared in the design.

Correction: Use selected-profile-compatible simple branch labels; declare and import PreparationFacts and compute it internally from the actual session. A completed private harness with simple labels generated and passed all six decision branches. This does not implement the proposal.

This is a reproduced failure on the current bounded pure frontend. Other stateful paths may accept different source forms; exact final profile selection remains mandatory.

### MT-02 (P2): semantic responsibility needs separation

Target: `GAPS.json D04/D05/D06; ReportMissingFields / AssessRevision / AssessPreparation`.

The index associates missing-field reporting with Query, but its described behavior derives findings from supplied document/schema observations. D06 does not separate check-strategy selection from derived readiness status.

Correction: Derive missing fields/revision impact/readiness in Calculations, reusable Boolean predicates in Rules, shape outputs with Mappings, and use Operations for guarding/recording actions. A Policy should select the preparation/check strategy. Reserve Query for retrieving an explicitly stored report/projection with declared keys and source.

### MT-03 (P2): persistence and Query contract incomplete

Target: `D02 lookup notes; D05 candidate draft; D07 acknowledgement Queries`.

Snapshot Value Objects are appropriate, but the proposal does not declare actual Query source Entity/key or authoritative write/replay ownership for new notes and acknowledgements.

Correction: Reuse the existing session journal as authoritative history and declare how its current Entity projection exposes new notes. CandidateDraft/Assessment/RevisionPlan remain immutable snapshots unless independent stable lifecycle identity is deliberately selected. No second truth store or unnecessary Entity is required.

### MT-04 (P2): public boundary and external observation contracts incomplete

Target: `D01/D02/D07 Interface and public Operations/Queries`.

Interface is named for lookup but no complete request/response/capability contract is declared. New commands/read surfaces lack an explicit choice of existing Entry payload versus new Entry and observer/caller attribution.

Correction: Complete the bounded-schema Interface and actual source-owner binding. Route new commands through the declared existing protected Entry or specify a new Entry with exact access contract. Distinguish declared local actor from authenticated host actor; source scope/standing/membership observations and acknowledgements cannot be certified by caller assertions.

### MT-05 (P2): optional Event not profile- or transaction-bound

Target: `GAPS.json D07 Event; default profile.json`.

D07 lists Event without an actual producer, past-fact payload, receiver, deduplication identity or atomic publication contract. The default authoring profile does not select Event; the separate preparation profile does.

Correction: Use a past fact such as HandoffRecorded or AcknowledgementObserved only after durable recording, with source/attempt identity and an explicitly selected Event profile/owner. File-envelope construction can remain pure with no Event. Do not assert atomicity across the CLI file journal and an independent SQLite outbox.

### MT-06 (P2): profile-bound qualification still missing

Target: `new Text and List<Binding,100> fields across D01/D02 and new snapshot types`.

Shared Text allows 262144 bytes, while selected native value frames are 32768 bytes and input/output are 65536. New evidence arrays and prose fields have no worst-case framing/capacity proof. This is an unqualified design obligation, not a newly observed runtime failure.

Correction: Use exact bound document/manifest references for large prose/evidence, bounded pages and capacity guards. Define every referenced technical type and select profiles/source manifests before claiming complete compilation. Preserve full original content without truncation or raising compiler limits.

## Per-type responsibility assessment

| Meta-type | Assessment | Correct use |
|---|---|---|
| Entity | Appropriate existing source; future boundary incomplete | Persisted independently identified state or an explicit read projection. Reuse Projection/session ownership; do not turn every immutable draft/result into a separate Entity. |
| Value Object | Appropriate | PreparationContext, lookup observations, assessments, revision plans, field contributions and handoff envelopes are immutable snapshots. An ID/reference field does not by itself require Entity. |
| Enum | Appropriate | Finite applicability, question target, next-action and readiness values fit. Payload variants are supported by the selected dialect; they are not an illegal custom meta-type. |
| Operation | Appropriate, contract incomplete | ValidatePreparationContext can legally reject/return without effects in this dialect. Recording notes/answers/revisions/handoffs requires exact guarded commit/replay ownership. Guard-only Operations are not automatically mislabeled Queries. |
| Query | Refinement required | Retrieve from a declared Entity/projection using exact source/key/predicate. Do not use Query as the computation of missing fields or as an undeclared direct filesystem/search effect. |
| Calculation | Use more explicitly | Derive facts, differences, missing fields and bounded assessment values. SelectAction is a legal pure helper; avoid claiming a Calculation retrieves external state or records a decision. |
| Rule | Use more explicitly | Reusable Boolean invariants: Work/project shape, exact binding consistency, revision partitions, candidate completeness, and handoff equality. Inline Operation guards remain legal. |
| Policy | Right intent; D03 syntax blocker | NextSemanticAction selects a semantic action and is a good Policy. Separate selection of a preparation strategy from calculation of readiness. A zero-effect enforced decision Policy is supported by the dialect. |
| Workflow | No new Workflow required by current design | The session loop may use commands, next-action Policy and existing lifecycles. Add a Define-owned Workflow only for explicitly selected durable multi-operation scheduling/recovery; shared Lab construction/admission/publication remain outside. |
| Interface | Right boundary; incomplete declaration | A logical bounded request/response contract for source lookup or handoff. It is not merely a field transform, implementation adapter, signing permission or a new universal Port meta-type. |
| Event | Optional; incomplete contract/profile | Past fact after a committed state change. Requires explicit emitter/receiver, payload identity, selected Event profile and delivery/replay semantics. A handoff command is not itself an Event. |
| Mapping | Appropriate | Project exact inputs into request/candidate/successor/handoff shapes. Do not hide owner choices, norm creation, validation or storage effects inside a Mapping. |
| State Machine | Existing reuse appropriate | QuestionLifecycle and SessionLifecycle represent valid transitions. NextAction is an advisory result enum/Policy, not itself a persisted state machine. New lifecycle transitions need explicit contracts if selected. |
| Entry | Additional boundary declaration; missing wiring | Entry is checked separately from the 13 DomainSpec backend meta-types. Every public operation/query must have a declared selected Entry path, access contract and custody rules; pure local CLI evaluation does not imply that authenticated Entry was exercised. |

## Proposed corrected decomposition

- D01: ValueObject context + reusable shape/source Rules + guarded validation Operation; shared Lab remains workspace/membership authority.
- D02: Interface for the actual source read contract; Operation records lookup/assessment in session history; Query reads its declared projection; Calculation/Mapping derive comparisons and summaries.
- D03: Enum for question targets and next action; Calculation derives actual session facts; Policy selects next action; Operation plans/applies the appropriate command; existing State Machines retain question/session transitions.
- D04: ValueObject revision plan; Calculation computes the proposed partition; Rule validates exact coverage/disjointness/predecessor; Mapping builds the successor; Operation commits via the existing session boundary.
- D05: ValueObject field contributions and snapshots; Calculation derives missing fields; Rules validate completeness/fidelity; Mapping assembles an explicit candidate; Operation records/publishes the candidate preparation. A Query can retrieve a stored draft/report but must not replace the calculation.
- D06: Policy selects Define-owned check strategy for a preparation use; Rules evaluate prerequisites; Calculation derives the assessment; Mapping formats it; a guarded Operation exposes it. External acceptance and authority remain outside Define.
- D07: ValueObject handoff + exact-input Rules + Mapping + Operation for durable recording. Query reads recorded state. Optional Event only after actual durable recording with a selected compatible profile and explicit delivery contract.

## Corrected policy form (isolated harness qualified)

```alchlang
value-object PreparationFacts:
  context_sufficient Bool
  open_questions UInt64
  required_concepts UInt64
  unhandled_concepts UInt64
  selected_draft_gaps UInt64

policy NextSemanticAction:
  input facts PreparationFacts
  result NextAction
  ordered-cases:
    pending when facts.open_questions > 0 -> SelectAction(value=NextAction.AwaitResponse)
    context when not facts.context_sufficient -> SelectAction(value=NextAction.ClarifyContext)
    empty when facts.required_concepts == 0 -> SelectAction(value=NextAction.DeclareConcept)
    unhandled when facts.unhandled_concepts > 0 -> SelectAction(value=NextAction.ResolveConcept)
    draft when facts.selected_draft_gaps > 0 -> SelectAction(value=NextAction.CompleteSelectedDraft)
    otherwise -> SelectAction(value=NextAction.ReviewPack)
```

The harness supplies the already proposed NextAction enum and SelectAction Calculation. This excerpt is not a full generated service or proof that caller-provided facts are trustworthy. Source/custody observation remains separately bound.

## Probe setup limitations retained honestly

PARSER-PROBES and GENERIC-FRONTEND-PROBES preserve the raw results. The first exact-context generation attempt used additional sources with a pure profile; the CLI rejected that unsupported combination. A following single-module attempt lacked a required pure declaration root and was refused. Those are probe setup/profile restrictions, not new production Define failures. Adding an explicitly identified Rule root yielded the successful isolated guard probe. No compiler limits, frozen Craft files, original owner handles or active source selections were modified to make probes pass.

All current design excerpts remain unchanged for review. Findings should be applied to a successor design/source selection before implementation. Existing runtime behavior and authority boundaries remain outside the scope of this audit's edits.
