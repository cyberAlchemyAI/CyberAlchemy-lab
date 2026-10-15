# Can the integrated Lab plan use only one approval?

## Scope and finding

The object is the whole integrated roadmap: source profiles and runtime; definitions, carriers and typed relationships; actor/action boundaries; engineering and research; evidence, classifications, failures, challenges and operational learning; ontology and selected migration; Product realization, adoption, pilot and release.

The original plan has four owner nodes: C10, W08, O06 and R08. The admitted governance model permits one interaction resolving several independent Decisions. Thus the number of planned reviews can be reduced. It does not follow that all operations, outcomes or future evidence can be covered by one pre-existing authorization.

| Claim | Finding |
| --- | --- |
| One continuous construction and candidate evaluation run | Feasible within a bounded authorized scope; failures may require repair cycles. “One shot” does not mean one unverified implementation pass. |
| One final review for all exact constructed admission targets | Supported by the admitted governance model; generic whole-package publication still needs implementation and proof. |
| All admitted operational milestones complete before that review | Unsupported unless prior authority already covers the required operational effects. |
| One response authorizes exact admissions and separately represented local instructions | Potentially feasible; actual roles, closed targets and effect/carrier fit must be established. |
| One Admission Transaction atomically activates, provisions and publishes everything | Incompatible with the current carrier: activations zero, external references empty. |
| All future Work and lessons automatically admitted by that response | Incompatible with exact-target authority; future targets require their own disposition. |
| Stable release guaranteed under exactly one checkpoint | Conditional; required evidence, scope and representable release conditions must exist. |

Current request authorizes this analysis. No execution authority is inferred from asking whether the plan can be executed with one approval.

## Evidence in the repository

- [D74](../../../decisions/0074-governance-transaction-surface-admission/DECISION.md) already records one response, three independent Decisions and one atomic admission, including deterministic State and history consequences. Activations/external effects were zero.
- The [Decision Bundle definition](../../../../authority/definitions/candidates/0003-single-decision-checkpoint/definitions/decision-bundle/v1/definition.json) preserves exact targets, independent roles and boundaries; excludes targets that do not yet exist. It is admitted through registry history even though its immutable source body retains candidate-era labels.
- [Workflow Decision Profile/v1](../../../../authority/artifact-types/workflow-decision-profile/v1/schema.json) supports `single` and `final-review`. A preference/profile selects a checkpoint; it does not grant authority.
- [Admission Transaction/v1](../../../../authority/artifact-types/admission-transaction/v1/schema.json) fixes `runtime_activations` to zero and `external_effect_refs` to an empty array. Its stable-core policy separates reviewed inputs from generated consequences.
- [Decision Bundle/v1](../../../../authority/artifact-types/decision-bundle/v1/schema.json) requires materialized targets and `all-or-nothing` atomicity. A mixed review must establish which authority records are admitted atomically and which later operations have separate execution semantics. One response cannot make physical/external execution globally atomic.
- [Candidate runtime operations](../../../../implementation/lab-runtime/v2/lab_runtime/operations.py) stage a full target closure and preserve independent target Decision cores. [Store planning](../../../../implementation/lab-runtime/v2/lab_runtime/store.py) still reports no repository-admission effect. C07 is the missing generic repository publisher; existing D75 publication is specific to that reviewed package.
- [Source verification](../../../../implementation/lab-runtime/v2/lab_runtime/sources.py) binds current lookup bytes. A final admission changes State/epoch: a profile transition must be designed and exercised rather than silently changing reviewed package bytes.
- Original [C11](../work-pack/tasks/C11.md), [W09](../work-pack/tasks/W09.md) and [R05](../work-pack/tasks/R05.md) have actual admission/authority/adoption requirements. Renaming a candidate demo cannot satisfy them.

Exact sources are bound in [SOURCE-BASELINE.json](SOURCE-BASELINE.json). The 121 current type / 41 Relation Kind coverage analysis remains the [original coverage matrix](../CONTRACT-COVERAGE.md).

## Phase changes

| Original task | Before the final checkpoint | Obligation after the checkpoint |
| --- | --- | --- |
| C10 successor admission | Prepare exact independent runtime/profile/contract members | A01 applies the selected repository effects. |
| C11 provisioning | Rehearse isolated candidate bootstrap; prepare exact real operator/store instructions | A02 provisions only the selected authorized local scope. |
| C12/C13 actual Work/continuity | Genuine authorized candidate Work, replay, restart and fresh-session evidence | A03 verifies admitted operation; candidate evidence remains attributed. |
| W08 workflow review | Prepare action/workflow/learning members | A01 admits selected targets. |
| W09 actual workflow/learning closure | Genuine candidate workflow and later lesson application evidence | A03 verifies the original operational criteria. |
| O06 ontology/import review | Prepare exact mappings, imports, source disposition and typed joins | A01 admits selected targets; any separate local operations follow A02. |
| O07 admitted coherence | Verify candidate reconstruction and coverage; retain explicit gaps | A03 checks admitted selected-scope coherence. |
| R04/R05 adoption and Product pilot | Prepare proposed bindings; gather genuine candidate-use evidence within authorized scope | A03 observes actual adoption and any required admitted pilot criteria. |
| R07/R08 release | Full package validation, final freeze and one complete review | A04 executes only an already authorized representable release action, or reports blocked release. |

All other construction tasks remain. The [machine transformation](task-transformation.json) covers every original node and retains its acceptance criteria. Six added nodes name required work: S01 candidate composition/bootstrap, S02 final preflight, A01 admission, A02 local operations, A03 operational closure and A04 release disposition.

The original 57 SWUs are retained as references, not silently treated as executable under altered input authority. Changed contracts must explicitly replace admitted prerequisites with candidate prerequisites for preparation, and preserve their operational obligations after admission.

## Implementation work needed to make this viable

### Candidate closure and bootstrap: S01

Build an isolated candidate catalog from staged definitions, type schemas, Relation Kinds, instances and independent source profiles. Validate exact versions, endpoint closure, qualifiers and typed-axis invariants against the whole proposed closure. Existing staging is useful, but a candidate initialization adapter and multi-layer candidate source composition are not established operational capabilities.

The adapter must preserve candidate provenance, prevent canonical lookup/State mutation, and distinguish rehearsal keys from real owner authority. Actual candidate-use experiments require an explicit development execution scope. Test fixtures prove only fixture behavior; genuine candidate Work may yield real evidence if the work and observations actually occur.

### Publisher and admission: C07 / S02 / A01

Implement a generic publisher that admits all selected exact repository targets as one recoverable authority unit. Verify mixed-target closure, preconditions, no partial admission, immutable committed postimage and deterministic mirror/index convergence. Local runtime staging is not this publisher.

Keep Definition/type/instance/Typed Relation/ontology Node/local Edge distinct. Preserve complete typed extension review, independently owned relations and exact endpoint pairs. Do not reduce semantic checks to accepting JSON shapes.

### Profile transition and hash closure: C01–C05 / S02

Freeze the executable and compatible profile protocol independently. Bind stable Decision cores to exact reviewed inputs; bind generated State/event/profile consequences in application receipts. Declare the compatible post-admission profile capture rule and exercise the precise transition. Any capture that changes semantic scope or software bytes beyond the declared rule invalidates review. Avoid a digest cycle where a profile hashes the admission containing that same profile.

### Operational and release carrier fit: C02 / R01 / S02

Establish exact records for authorizing and executing local provisioning, adoption, actions and selected release effects. The final Bundle must preserve its all-or-nothing authority semantics; A01 cannot contain activation/external effects. Separately attributable execution units need explicit order, prerequisites, stop behavior and rollback. If the existing model cannot represent a selected effect, materialize the proposed extension as a reviewed target in the candidate; do not invent a new authority interpretation after approval.

Conditional execution instructions are possible only when the chosen carriers and authority semantics support them. A future evidence-dependent semantic Decision cannot be substituted with a generic “release if it looks good.” R01 must identify whether genuine candidate pilot evidence satisfies release acceptance. If newly admitted operation is a mandatory evidence basis, and no prior authority permits obtaining it, the full-release single-checkpoint route remains blocked.

## Final review package

One navigable presentation contains an overview, revised definitions/schemas, relationship and endpoint changes, examples, exact source/package/evidence manifests, pilot results, private/public boundary, member-owner-effect matrix, execution order and rollback/stop conditions. Independent members cover the selected runtime/contracts/profiles, workflow/learning model, ontology/imports, bindings/adoption, local operational instructions and release scope.

S02 checks every target exists, each owner role belongs to the answering principal, every effect is scoped, evidence is attributable, reviewed bytes and current base match, hashes are acyclic and the publisher/carriers have been proved. Unresolved future targets cannot enter the Bundle. The current proposal intentionally has no completed Bundle or selected outcomes.

One actual response then resolves the selected exact members. The response does not merge their authorities. A rejection, missing owner or changed target stops application; all-or-nothing admission must not silently apply an accepted subset.

## After approval and the future-target limit

A01 applies exact repository authority and deterministic consequences. A02 executes independently scoped local instructions. A03 checks actual operational obligations. A04 performs only the exact selected release action whose declared conditions are satisfied.

Generated State, event appends, receipts, indexes and projections already declared by the package do not require a new bookkeeping approval. Later observations are evidence of what occurred; they do not automatically become admitted semantic artifacts.

The runtime signs proposals against exact targets, scope and current local head. A final approval cannot pre-sign transactions for unknown future Work, failure assessments or lessons. New semantic targets, changed executable bytes, new operational effects or a newly required release Decision require renewed review. If the original milestone requires admission of such newly produced targets, preserve it as pending; do not call the full roadmap complete.

## Realistic example

We construct a complete candidate Lab package, including action boundaries, engineering/research flows, failure classification, challenge handling, lesson selection and ontology projections. Within an authorized isolated development scope, a genuine change task exposes a failure, records evidence, yields a candidate lesson and applies that lesson to a later genuine task. A candidate Product pilot measures whether its user can reconstruct current project state and trace the relevant decisions.

Those existing artifacts, exact contracts and pilot evidence can all enter one final review. An ephemeral Agent receives a Context View and Ontology View from candidate Project State; its session memory expires. Durable lessons live in project artifacts with explicit status, rather than in an Agent identity.

After the response, selected targets become admitted together. The separately authorized local store is provisioned and verified against the resulting source profile. A later real failure creates a **new** candidate assessment/lesson: that new content was absent from the approved targets and is not automatically admitted. If a required pilot must occur against the newly admitted store, its observation remains an outstanding release condition; a newly needed semantic release decision means the original full-release one-checkpoint promise cannot hold.

## Readiness and recommendation

Planning feasibility: **flag, conditional**. Construction and a final admission review can be consolidated; literal admitted completion before approval cannot. The next implementation route is to reconcile C01/C02/R01 and the variant task/SWU contracts, then build candidate composition, publisher and profile-transition proofs within the authorized execution scope.

Preserve the one-checkpoint target. Stop and report a specific unmet prerequisite if exact target readiness, pilot evidence, owner authority or carrier fit prevents it. Do not replace those conditions with extra automatic approvals or weaken the complete Lab scope.
