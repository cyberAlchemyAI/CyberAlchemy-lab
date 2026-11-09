# Define AlchLang meta-type audit

**Result: the meta-type vocabulary is covered, but semantic/integration use is not fully correct.**

Reviewed all 33 maintained authored files and 209 declarations. All 13 supported backend meta-types occur; Entry contributes six additional transport declarations. Presence is inventory, not a correctness or completeness proof.

The audit also checked the selected AlchLang 0.7.0-candidate.0 / Craft Core 1.3.0 contracts. Payload-bearing enums and zero-effect Operations are legal in that dialect. Broader DomainSpec cards alone are insufficient to label them illegal. No UI meta-types or superseded Saga are required for this backend model.

No implementation or canonical definitions were changed. Generated-code probes used isolated fixture grants/stores only.

## Findings

### P1 META-01: Preparation steps are not bound to the persisted run context

**Observed:** A run created for project:context-management accepted a preparation session for project:foreign with an all-zero source digest; continuation then returned kind=complete.

**Implication:** Correlation by numeric id does not preserve the actual Project/Work/source selection across the workflow boundary. Fixture grants allowed the entry calls; this is not evidence of a deployed authorization exploit.

**Correction:** Bind each stage and continuation to the exact stored PreparationRun, source selection and candidate revision/attempt. Enforce scope/source invariants in the authored operations and authenticated host contract.

Evidence: `workspaces/products/define/implementation/cli/alchlang/preparation.alch:10`, `workspaces/products/define/implementation/cli/alchlang/preparation.alch:115`, `workspaces/products/define/implementation/cli/alchlang/preparation.alch:41`.

### P1 META-02: The event/review handoff drops candidate attempt identity

**Observed:** PreparedCandidate accepted (id=81,attempt=1) and (id=81,attempt=2). PreparedNotice carries id but no attempt. The first relay delivery committed and the second returned unavailable. ReviewRequest uses identity id only.

**Implication:** The consumer cannot identify the exact candidate revision from the notice; distinct candidate attempts collide at the review identity. The relay result does not expose a detailed cause, so it is retained as unavailable rather than reported as a proven specific exception.

**Correction:** Carry exact candidate identity/attempt and an immutable request or artifact binding in the event and receiver. Separate deduplication of one event occurrence from admission of a genuinely different candidate revision.

Evidence: `workspaces/products/define/implementation/cli/alchlang/preparation.alch:136`, `workspaces/products/define/implementation/cli/alchlang/preparation.alch:101`, `workspaces/products/define/implementation/cli/alchlang/modules/lab-integration/use-cases/receive-candidate.alch:8`.

### P1 META-03: Cross-list source consistency is missing from preparation eligibility

**Observed:** BindEvidence accepted shared.json with digest b while source_bindings already selected shared.json with digest a. ExportPreparation returned a Prepared request containing both.

**Implication:** The AlchLang preparation gate permits an internally inconsistent source cut. The old Python engine may refuse it later; that later defense does not make the authored gate complete.

**Correction:** Add one source-cut consistency Rule across source, evidence, lineage and selected materialization bindings; enforce it before accepting conflicting edits and before export/preparation.

Evidence: `workspaces/products/define/implementation/cli/alchlang/modules/work/use-cases/bind-inputs.alch:9`, `workspaces/products/define/implementation/cli/alchlang/modules/work/use-cases/bind-inputs.alch:59`, `workspaces/products/define/implementation/cli/alchlang/modules/packs/shared/preparation.alch:56`.

### P1 META-04: Confirmation records caller assertions without an authored package-match gate

**Observed:** ConfirmCandidate accepted arbitrary package/request hashes on a newly initialized session with no evaluated context or handled concepts, as long as the authored actor strings matched.

**Implication:** The current CLI performs the real package inspection/match outside the model. A directly invoked generated Entry can record an unverified confirmation. This is candidate confirmation, not semantic-owner admission or a granted native permission.

**Correction:** Represent verified exact package/request correspondence as a source-bound input contract and authored eligibility Rule. Keep generic byte observation in adapters; keep the confirmation acceptance decision in AlchLang. Bind actor attribution to the applicable host identity where required.

Evidence: `workspaces/products/define/implementation/cli/alchlang/modules/packs/use-cases/confirm-candidate.alch:23`, `workspaces/products/define/implementation/cli/alchlang/runtime/cli.mjs:105`.

### P2 META-05: Bounded collection transitions fall through to runtime resource failures

**Observed:** Asking for another concept with 24 existing required concepts produced OutputBound in QuestionConcepts, with failed-before-write, instead of a business rejection.

**Implication:** The runtime fails closed, but valid boundary input is not covered by the declared business transition. total=true on a Mapping is not a replacement for capacity preconditions.

**Correction:** Add capacity Rules to the owning Operations before bounded append/upsert, including questions, responses, concepts, handling, inputs, applications, assessments and selections. Preserve distinct business refusal outcomes.

Evidence: `workspaces/products/define/implementation/cli/alchlang/modules/conversation/use-cases/ask-question.alch:13`, `workspaces/products/define/implementation/cli/alchlang/modules/conversation/use-cases/ask-question.alch:26`, `workspaces/products/define/implementation/cli/alchlang/modules/conversation/use-cases/ask-question.alch:33`.

### P1 META-06: The maintained authored model is not the sole execution source

**Observed:** The CLI session runtime builds from a frozen older model. Pack preparation, inspection, materialization and reconstruction invoke standalone Python. New pack-engine components are separately verified and not fully wired into the public workflow.

**Implication:** Correct declarations in the 33 maintained files cannot establish correctness of a different executed source. The AlchLang-only migration and engine deletion gate remain incomplete.

**Correction:** Make new Work execute the selected maintained model, define an exact predecessor replay route or explicit refusal for old journals, and port/wire remaining behavior before deleting predecessor dependencies.

Evidence: `workspaces/products/define/implementation/cli/alchlang/runtime/build.mjs:7`, `workspaces/products/define/implementation/cli/alchlang/runtime/build.mjs:11`, `workspaces/products/define/implementation/cli/alchlang/runtime/cli.mjs:45`.

### P2 META-07: The new PackEngine Binding is a divergent carrier

**Observed:** Define.Shared.Binding includes digest_kind=original-file-sha256 and a 256-byte Ref; Define.PackEngine.Binding omits digest_kind and uses a 1024-byte Ref.

**Implication:** The value objects are legal in isolation but are not interchangeable contracts. Exact original-file versus selected-entry digest meaning is weakened unless the bridge preserves and checks that distinction.

**Correction:** Reuse a shared carrier or declare an explicit source-bound representation mapping and separate original-file/selected-entry binding types with agreed limits. Do not silently alias them.

Evidence: `workspaces/products/define/implementation/cli/alchlang/pack-engine.alch:58`, `workspaces/products/define/implementation/cli/alchlang/shared/values.alch:29`, `workspaces/products/define/implementation/cli/alchlang/pack-engine.alch:3`, `workspaces/products/define/implementation/cli/alchlang/shared/values.alch:3`.

## Meta-type coverage and fit

| Meta-type | Declarations | Assessment |
|---|---:|---|
| Entity | 5 | Appropriate persisted identities, with run/attempt/review correlation defects. |
| Value Object | 59 | Appropriate snapshots/observations/contracts; clarify durable aggregate boundary and Binding drift. |
| Enum | 29 | Valid closed values and supported payload variants; narrow open business tags where appropriate. |
| Operation | 33 | Valid command and transition surfaces, including zero-effect validation; several preconditions are missing. |
| Query | 1 | ReadProjection is read-only; its selectors are not membership authorization. |
| Calculation | 37 | Pure derived values/extractors fit; resource bounds remain part of the effective contract. |
| Rule | 9 | Existing predicates fit; source-cut, confirmation and capacity gates are incomplete. |
| Policy | 2 | Continuation strategy and enforced eligibility are supported; no authority is created. |
| Workflow | 1 | Recovery/correlation is declared; exact stored context and candidate linkage need correction. |
| Interface | 5 | Supported bounded-schema exposure; distinct from runtime permission. |
| Event | 1 | Past typed-candidate commit is appropriate; exact subject attempt is lost. |
| Mapping | 19 | Pure transforms/constructors are supported; capacity and state-transition assumptions need explicit guards. |
| State Machine | 2 | Question and Session transitions are declared and called. No requirement to use a machine for every record. |
| Entry | 6 | Additional executable transport syntax, not a fourteenth DS-D1 backend concept; six protected boundaries are declared. |

## Classification notes

- **DESIGN-01 (Entity, Value Object):** Session, Question and Response may legitimately be immutable snapshots/value records. An id field alone does not make a Value Object wrong. However, durable Session/Work identity, lifecycle, journal authority and snapshot reconstruction need one explicit aggregate contract in the authored model; Projection is a disposable cache, not that contract. Reuse existing durable storage rather than adding a second store merely to obtain an Entity declaration.
- **DESIGN-02 (Rule, Operation):** All nine new Verify* Operations are accepted zero-effect commands with named refusal outcomes in this dialect. They are not compiler errors and should not be changed to Queries merely because they do not write. Reusable boolean eligibility should be factored into Rules; wrappers remain Operations where an explicit validation-command protocol is intended.
- **DESIGN-03 (Calculation, Policy):** UseReadiness computes a classification value, so Calculation is defensible. ContinueLab selects a continuation strategy and is a clear Policy. PreparationEligibility is a supported Allow/Reject enforcement Policy; extracting a reusable eligibility Rule is optional layering, not evidence that this Policy is illegal.
- **DESIGN-04 (Enum):** Payload-bearing enum variants are explicitly supported algebraic data types in the selected AlchLang frontend, despite the broader DomainSpec card describing flat enums. Retention posture, embedded entry kind and completion kind currently use open Ref/String carriers; closed enums or literals would make intended finite sets clearer where the runtime ABI permits.
- **DESIGN-05 (Interface, Entry):** The five bounded-schema Interfaces are supported schema/exposure contracts. The six Entries are concrete transport/authentication boundaries. Neither an Interface declaration nor Project/Work query filters authenticate native membership or grant owner authority.
- **DESIGN-06 (Mapping, State Machine):** Mappings used as immutable Session constructors are accepted by the language. Some include revision/upsert/lifecycle decisions, so their role as state-transition construction should be explicit and guarded by Operations/Rules/State Machines rather than described as mere format conversion. Both existing State Machines are actually invoked; using additional lifecycle machines should follow real transition requirements, not a target count.

## Recommended order

1. Bind Workflow stages to exact run/context/source and carry exact candidate identity into the Event and review receiver.
2. Add authored Rules for the complete source cut, confirmation correspondence and collection capacity.
3. Resolve snapshot/aggregate and binding-carrier contracts explicitly. Preserve correct Calculation/Rule/Policy distinctions rather than converting every validator indiscriminately.
4. Wire the maintained model and the remaining Pack workflow through generic adapters. Keep exact predecessor replay separate.
5. Re-run the focused negative cases and the complete replacement workflow before retiring Python/legacy sources.

## Evidence and limits

- [Complete file/declaration inventory](INVENTORY.json).
- [Machine-readable findings and design notes](FINDINGS.json).
- [Actual generated-code reproduction results](REPRODUCTIONS.json).
- [Pinned language/meta-type source references](SOURCES.json).

The confirmed capacity case failed before write. The relay returned unavailable for the second candidate notice; the API did not expose a more specific reason. Candidate confirmation is not owner admission. Fixture authentication does not qualify production Project membership or repository authority.
