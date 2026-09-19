---
title: ARE Interaction Learning Loop — One-Shot Implementation Plan
plan_id: ARE-INTERACTION-LEARNING-001
revision: 2
status: proposed-for-implementation
updatedAt: 2026-09-04
route_id: CA2-ROUTE-PLAN
work_lane: product-construction
owner: Agent Reasoning Engine product owner
product_ref: CA2-PRODUCT-AGENT-REASONING-ENGINE
ontology_id: cav2.agent-reasoning-engine.bridge.v1
authority_effect: none
---

# ARE Interaction Learning Loop

## Product outcome

ARE should reuse the reasoning state that explains what the user means, what
the work requires next, and how the user wants the result expressed. It should
learn from corrections without treating every utterance as a permanent
preference or making the user read its internal labels.

Make **Manage Interaction Context** a first-class capability within ARE. Extend
the existing intent, reflection, context, and reasoning-state components; do not
build another interpreter, memory service, or agent runtime.

Its operating mechanism is the **Interaction Learning Loop**: interpret from
reusable reasoning state, act, observe the result, diagnose a mismatch, repair,
apply a scoped lesson later, and measure whether that lesson helped. Recurring
failures and lack of progress feed ARE's existing research/experiment loop.

Revision 2 replaces the component-first implementation sequence with this
complete feedback cycle. The original five context records remain; two further
records bind lesson application to outcomes and assess learning progress. Reuse
Reflection for scoped lessons and existing evolution records for hypotheses,
experiments, and learning decisions. Do not create a parallel research system.
These are definition drafts, not a generated Define Pack or canonical changes.

Current scope is design planning. Implementation and tests below are future
work. No runtime, historical binding, acceptance record, or serving profile is
changed by this document.

## 0. The process being implemented

### Two connected feedback cycles

```text
selected reasoning state + request
  -> interpretation and expected result
  -> route + bounded action
  -> observed result and attributed feedback
  -> mismatch assessment
  -> keep, repair, or revise scoped reasoning state
  -> select and apply a lesson on a later applicable request
  -> assess its observed outcome -> next state

recurrence / counterevidence / no gain / explicit reflection request
  -> measurable improvement target
  -> existing hypothesis + research + experiment pipeline
  -> comparison with baseline and protected checks
  -> retain or reject the experimental change
  -> measured evidence feeds the next learning cycle
```

The work loop changes current interpretation and permitted retained state. The
evolution loop tests changes to the engine. Neither a stored lesson nor a model's
account of success proves an improvement. The serving engine stays on its
current version throughout this implementation and its canaries.

### Trigger, comparison, update, and stop contract

| When | What the loop does | Evidence and next state |
| --- | --- | --- |
| `turn/start` | Recover current selected state; interpret the new request; resolve references and causal continuation; select applicable lessons and preferences. | Freeze the interpretation, expected observable result, selected lesson revisions, policy, and context before dispatch. Obvious requests require no extra model call. |
| Before dispatch | Check currentness, source roles, constraints, material ambiguity, and projection budget. | At most one interpretation-driven refinement. Ask or block when material uncertainty remains; do not loop on the same input. |
| `turn/completed` or a bound artifact/test observation | Compare the observed result with the declared checks for that interpretation. | Append supported, contradicted, or inconclusive outcome evidence. No applicable check or missing output means inconclusive, not success. |
| A user correction, edit, rejection, or explicit reflection request | Bind the feedback to the exact earlier turn/artifact; distinguish misunderstanding, execution failure, new preference, changed requirement, and environment drift. | Repair the current request immediately when supported; append the explanation and scoped lesson candidate. Ambiguous feedback attribution stays unresolved rather than silently blaming the last turn. |
| A later applicable request | Project a permitted lesson and record whether it reached the model. | Create an application assessment bound to the lesson revision, request, envelope, and dispatch. Selection is not application; dispatch is not compliance. |
| A later result or further correction | Evaluate that application against its expected benefit and counterexamples. | Support, revise, suspend, or retain the lesson as unproven. Reusing familiar wording or receiving no complaint earns no success credit. |
| Repeated failure, stagnation, or an explicit improvement request | Produce a progress assessment and, if permitted, a deduplicated improvement target. | Use the existing evolution pipeline. Missing providers yield a visible research-pending result, not invented research or a stalled ordinary conversation. |

Keep source evidence types distinct: a test can establish its tested property;
user feedback can establish the expressed correction; a model judgment is a
diagnostic proposal. Task success, preference adherence, and effect permission
must never substitute for one another. Existing semantic evaluation remains
opt-in for configured domains; this loop does not fabricate semantic inputs.

### The reusable lesson

Extend Intent Reflection into a versioned lesson-bearing record containing:

```text
situation and scope
previous interpretation and the evidence used
observed mismatch and its source
revised interpretation / proposed repair
applicability conditions and exclusions
expected observable benefit and falsifier
supporting evidence, counterevidence, and unresolved alternatives
user retention/application policy
predecessor revision and subsequent application references
```

Application references are appended through separate records; earlier
reflections are not mutated to add later outcomes. The existing completed-turn
frontier is the experience anchor. Do not add a duplicate experience store.

For this conversation, the local correction is “explain the operating loop
before continuing the component design.” A possible general hypothesis is
“process-first explanations reduce corrective exchanges for feedback-system
design.” Neither supports “this user dislikes definitions.” The benchmark must
include an explicit definitions-first request as a counterexample.

### Concrete V1 defaults

These are proposed engineering defaults for this implementation, not findings
from the cited research. Put them in a validated profile and freeze them in each
experiment manifest; do not tune them after seeing holdout results.

| Control | Default |
| --- | --- |
| Integration | Disabled in existing serving profiles. A dedicated test profile enables the complete loop. |
| Ordinary enabled use | Immediate correction is independent of learning; inferred lessons are observed within the current interaction until `apply-scoped` is selected. No cross-user or account-wide learning. |
| Fast-path work | Deterministic selection/currentness/assessment only; at most 50 optional active lesson/preference records and the existing shared 32 KiB inline ceiling. Mandatory constraints are never dropped to satisfy the record cap. |
| Model work | Zero additional calls on an obvious request. At most one configured interpretation/reflection call per triggering turn; no recursive self-critique. Unused call budget is not accumulated. |
| Failed lesson reuse | Two distinct contradicted applications among its latest five evaluable applications suspend that inferred lesson and propose revision. One explicit revocation or scope/safety violation excludes it immediately. |
| Recurring engine weakness | Three distinct attributed failures in the same scoped failure class among the latest 20 completed interactions can open one improvement target. A user may explicitly request reflection earlier. Count unique episodes, not duplicate notifications. |
| Unknown outcomes | Preserve inconclusive results and coverage counts. Exclude them from success-rate denominators; never manufacture a gain or retry merely because feedback is absent. |
| No gain | After two consecutive controlled attempts fail to exceed the preregistered minimum useful delta, stop the current strategy and request research/revision. Protected-check failure rejects the attempt immediately. |
| Experiment bound | At most three distinct hypotheses/attempts and one research cycle per target in one invocation. After exhaustion, return `stopped-no-gain` or `budget-exhausted` with all results. Identical attempts are not new hypotheses. |
| Research bound | Declared providers only; at most two providers and five results per provider. No raw conversation or private artifact text in external queries; query a redacted problem description. No provider means `research-pending`. |
| Concurrency and replay | One existing evolution scheduler, plus a ledger-backed trigger/outbox adapter. Checkpoint trigger and completion identities. Ambiguous post-crash delivery is `delivery-unknown`, not an automatic external retry. |
| Upgrade behavior | Recommend-only. Keep/reject experimental changes and preserve results; do not change the serving pointer. |

Progress comparisons require the same metric, evaluator, scenario cohort,
baseline, and policy. A changed comparator creates a new comparison identity,
not evidence that a strategy improved. Production observations identify a
possible benefit or failure; controlled comparisons establish treatment gains.

## 1. What the current design already supplies

| Existing element | Reuse | Gap to close |
| --- | --- | --- |
| [Intent Contract and User Control Profile](../../../../implementation/agent-reasoning-engine/packages/request-intent-runtime/src/contracts.mjs) | Objective, target, construction versus surface directives, referents, assumptions, visibility, correction retention. | Referents are plain string mappings; there is no typed grounding or scoped communication-preference contract. |
| [Intent compiler](../../../../implementation/agent-reasoning-engine/packages/request-intent-runtime/src/compiler.mjs) | Deterministic fast path and an optional provider boundary. | General discourse interpretation must not depend on adding another phrase-specific rule for each observed mistake. |
| [Reflection](../../../../implementation/agent-reasoning-engine/packages/request-intent-runtime/src/reflection.mjs) | Corrections, changed mind, new preference, predecessor/successor contracts, improvement eligibility. | Bind learning to exact evidence and applicability; do not equate an edit with a verified diagnosis. |
| [Continuation projection](../../../../implementation/agent-reasoning-engine/packages/codex-app-server-wrapper/src/continuation.mjs) | Objective frontier and distinct causal/opportunity markers. | Short-reference matching and a selected proposal do not cover general discourse focus and reference resolution. |
| [Codex turn preparation](../../../../implementation/agent-reasoning-engine/packages/codex-app-server-wrapper/src/wrapper.mjs) | Preflight, frozen context, intent compilation, reasoning dispatch. | Intent compilation runs after preflight, so it cannot currently resolve a request that preflight has already gated. |
| [Codex intent lifecycle](../../../../implementation/agent-reasoning-engine/packages/codex-app-server-wrapper/src/intent-lifecycle.mjs) | Opt-in compilation and an inline intent fragment. | The compiler receives context digests/source references, not the bounded selected meanings needed for interpretation. |
| Context Envelope and Reasoning State | Immutable projections, selected-dependency checks, append-only products and replay. | Add interaction products to these existing mechanisms, including recovery and shared projection budgets. |
| [Evolution runtime](../../../../implementation/agent-reasoning-engine/packages/evolution-runtime/README.md) | Improvement Signals, Research Hypotheses, observations, experiments, Learning Decisions, variant comparisons, and a one-cycle scheduler. | Bridge attributed interaction outcomes into these records without inventing research evidence or duplicating scheduling. |
| [Existing gain-gated experiments](../../../../implementation/agent-reasoning-engine/benchmarks/real-reasoning-v1/src/scorer-loop.mjs) | Declared strategies, protected checks, minimum gain, and no-gain stopping. | Reuse this comparison behavior for interaction experiments; production lesson applicability needs a separately bound assessment. |

The current completion path's Intent Realization Assessment can check visible
constraints, but a `satisfied` result without relevant checks is not proof of
understanding. The new outcome adapter must report check coverage and remain
inconclusive when the required evidence is absent. Historical v1 results retain
their original meaning and bytes.

The [existing intent/reflection plan](../../intent-reflection-implementation-dag.md)
already describes interpretation before committed routing. Its implementation
checkpoint must not be read as proof that the current wrapper has that ordering.
This plan makes that unfinished integration explicit.

The [six-view architecture](../../design/ARCHITECTURE.md) documents the semantic
evaluation boundary. Add an interaction-preparation view ahead of it; do not
replace its Problem Frame projector, evaluator, or receipt ownership. Historical
ACI integration decisions remain unchanged. This work extends the existing
local reasoning-state ledger and does not claim a new integrated ACI writer.

## 2. Definition coverage

### Seven record definitions derived from the loop

| Record | Define disposition | Proposed meaning and minimum content |
| --- | --- | --- |
| `are.interaction-state/v1` — Interaction State | propose | An explicit, replayable state of a conversation's active purpose, focus, scoped referent bindings, preferences, corrections, and unresolved interpretations. Bind participant, product/context scope, source events, predecessor, and digest. This is not hidden model reasoning or a second event store. |
| `are.interaction-context-view/v1` — Interaction Context View | specialize | A bounded immutable interaction-focused projection of the existing Context Window View. Bind the state digest, request, consumer, selected items and dependencies, application assessments, exclusions, conflicts, gaps, freshness, policy, and byte count. It contributes to the Context Envelope rather than bypassing it. |
| `are.grounding-assessment/v1` — Grounding Assessment | propose | An evidence-bound assessment of whether a particular interpretation or shared reference is sufficiently established for the current purpose. Record the proposition, participants, evidence spans, scope, and explicit, inferred, contested, unresolved, or superseded posture. Structural validity or model confidence cannot establish user agreement. |
| `are.communication-preference/v1` — Communication Preference | propose | A scoped preference about how information should be expressed to a particular recipient in a particular setting. Record subject, audience, output target, expression, conditions, explicit/inferred evidence, temporal scope, strength, and revision links. Distinguish positive, negative, relative, and exclusive forms without confusing form with strength. |
| `are.preference-application-assessment/v1` — Preference Application Assessment | propose | A request-bound explanation of whether and why a preference should influence this response: applicable, inapplicable, overridden, conflicted, disabled, or unsupported. Bind preference, current instruction evidence, policy, and selected state. Selection/projection is not proof that the resulting answer complied. |
| `are.lesson-application-assessment/v1` — Lesson Application Assessment | propose | Bind a specific retained reflection revision to a later request, selected context, dispatch, expected observable benefit, and outcome evidence. Distinguish not-applied, dispatched-awaiting-evidence, supported, contradicted, and inconclusive. Later evidence creates a successor assessment; dispatch does not prove compliance or causal benefit. |
| `are.interaction-learning-progress/v1` — Interaction Learning Progress Assessment | propose | Bind a unique cohort of episode/application identities, coverage, metric/evaluator/baseline/policy, failures, gains, and consumed budget to one disposition: observe, retain, revise, research-required, suspended, or stopped. This record triggers the existing evolution process; it does not replace its Learning Decision or authorize an upgrade. |

Draft boundaries and examples:

- **Interaction State:** “the page” can refer to an exact page from the active
  exchange. It cannot silently bind to a similarly named page from another
  product or another person.
- **Interaction Context View:** the model gets the useful meaning and evidence
  references, not just a digest and not the complete event history. The stable
  Context identity is not recreated each turn.
- **Grounding Assessment:** a user's correction supports the corrected referent.
  An assistant's unsupported “we agreed” does not establish a conceptual pact.
- **Communication Preference:** “keep the explanation concise” need not apply to
  the documentation being authored. How a person writes is not automatically
  how they want the assistant to write.
- **Preference Application Assessment:** an older general preference for brevity
  can be inapplicable to today's explicit request for a detailed explanation.
  The source and reason remain inspectable even when the response is quiet.

### Reuse and extend instead of multiplying concepts

| Meaning | Handling |
| --- | --- |
| Intent, Context, Product Capability | Reuse canonical CAV2-D39, CAV2-D66, and CAV2-D67. Context is a stable owner-qualified boundary, not a prompt or a per-turn view. |
| Context Window View, Context Item, Context Envelope | Reuse the [Context Basis definition pack](../../CONTEXT-BASIS-DEFINITION-PACK.v1-candidate.json) and current product meanings. Specialize view projection, preserving explicit identity lanes. |
| Conceptual pact | Represent as a scoped typed referent binding plus grounding evidence. A local shared use of a word does not redefine its canonical meaning. No separate pact runtime is needed in this vertical. |
| Discourse move and focus | Add defined fields to the Intent Contract: instruction, question, correction, preference, example, or reference; active purpose and referents. Mixed moves remain possible within one utterance. |
| Discourse cue versus causal marker | A cue such as “next,” “this,” or “now” helps locate a reference. Existing causal markers represent obligation/dependency evidence; opportunity markers represent optional improvements. A cue, ranking, or preference cannot manufacture a causal edge. |
| Correction, reflection, user controls, causal/opportunity markers | Record their existing runtime meanings in the definition/model alignment. Extend only where evidence, scope, or control semantics are missing. Do not present existing records as newly implemented. |
| Interaction Learning Loop, scoped lesson, and experience | Define the workflow from section 0. Specialize existing Intent Reflection as the scoped lesson; use the completed Reasoning State Frontier as the experience anchor. No second reflection, experience ledger, or learner scheduler. |
| Improvement Signal, Research Hypothesis, Hypothesis Observation, Research Experiment, Learning Decision, and Variant Comparison | Reuse the existing evolution records. Bind observed outcomes, exact code-pattern targets, falsifiers, and negative results through an interaction adapter. |

The next Define Pack must cover all these dependencies, not only the seven
records. Use Define's [existing output contract](../../../../define/docs/DEFINITION-PACK.md):
one disposition per concept, full definition voices, exact sources, relationships,
owners, examples, counterexamples, and visible open questions. Do not allocate
canonical D-numbers or change source digests merely to make a stale binding pass.

### Small ontology scaffold

```text
User utterance -> expresses -> Intent
Discourse cue -> helps resolve -> Referent binding
Grounding Assessment -> supports or contests -> Referent binding
Interaction State -> retains -> Referent binding
Interaction State -> retains -> Communication Preference
Preference Application Assessment -> selects for request -> Communication Preference
Interaction Context View -> projects -> Interaction State
Context Envelope -> includes -> Interaction Context View items
Intent Contract -> informs -> Route Decision
Causal Marker -> identifies dependency of -> Objective
Correction -> revises -> Interaction State
Intent Reflection -> proposes -> Improvement Signal
Intent Reflection -> carries -> Scoped lesson
Lesson Application Assessment -> tests later use of -> Scoped lesson
Outcome evidence -> supports or contradicts -> Lesson Application Assessment
Interaction Learning Progress -> assesses -> Lesson Application Assessment
Interaction Learning Progress -> triggers -> Improvement Target
Research Experiment -> tests -> Research Hypothesis
Variant Comparison -> feeds back into -> Interaction Learning Progress
User Control Profile -> limits -> Retention and application
```

These are proposed business relationships, not newly admitted ontology edges.

## 3. Research translated into design choices

The design choices below are ARE's interpretation of the research, not claims
that those papers implemented or validated this engine.

| Reference | Useful idea | Concrete use and limit |
| --- | --- | --- |
| [Grosz and Sidner, 1986](https://aclanthology.org/J86-3001/) | Separate discourse structure, intention, and attention. | Keep focus/reference cues distinct from objective and dependency records. Salience is not causality or permission. |
| [Clark and Brennan, 1991](https://www.cs.cmu.edu/~illah/CLASSDOCS/Clark91.pdf) | Ground understanding sufficiently for the joint task. | Ask when unresolved interpretation changes the material action; do not request confirmation for every harmless reference. Keep evidence of understanding, not assumed universal agreement. |
| [Brennan and Clark, 1996](https://web.stanford.edu/~clark/1990s/Brennan,%20S.E.%20_%20Clark,%20H.H.%20_Conceptual%20pacts%20and%20lexical%20choice%20in%20conversation_%201996.pdf) | Partner-specific conceptual pacts. | Scope shared labels to participants and purpose, with revision and challenge. Do not overwrite canonical definitions. |
| [Schegloff, Jefferson, and Sacks, 1977](https://doi.org/10.2307/413107) | Conversation repair distinguishes trouble and correction. | Extend existing correction/reflection records. Separate changed requirements and changed preferences from engine mistakes. |
| [Goodman and Frank, 2016](https://langcog.stanford.edu/papers_new/goodman-2016-underrev.pdf) | Pragmatic interpretation considers purpose and context under uncertainty. | Supply selected context to the existing optional interpreter. Do not add recursive model calls or treat a confidence score as verified intent. |
| [PRELUDE/CIPHER, 2024](https://arxiv.org/abs/2404.15269), [repository](https://github.com/gao-g/prelude) | Learn contextual textual preferences from edits and retrieve relevant ones. | Produce source-bound preference candidates from corrections. Preserve edit context and counterexamples; an edit is not self-proving preference evidence. |
| [PrefEval, 2025](https://arxiv.org/abs/2502.09597), [repository](https://github.com/amazon-science/PrefEval) | Test explicit/implicit preferences over conversational distance. | Add delayed relevance and non-applicability tests after a pinned dataset/license check. |
| [RealPref, 2026, v2](https://arxiv.org/abs/2603.04191v2), [repository](https://github.com/GG14127/RealPref) | Vary how preferences are expressed and test transfer. | Use expression/constraint distinctions, but do not copy its visible preference-awareness rubric unchanged: quiet ARE responses should not need to announce personalization. Its synthetic setup does not establish performance on our users. |

Reuse concepts and, where compatible, licensed fixtures. Do not import whole
research stacks before measuring the smallest integration.

## 4. Runtime design

### Ownership and proposed operations

| Existing owner | Design change |
| --- | --- |
| `request-intent-runtime` | Own interaction records, the state reducer, grounding, scoped lesson/application semantics, bounded projection, outcome coverage, and source-verified optional extraction. Reuse intent/correction provider boundaries. |
| `reasoning-state-runtime` | Persist the new products through its existing append-only event/checkpoint/replay mechanisms. No second journal or independently mutable profile database. |
| `context-basis-runtime` | Include selected interaction items in the frozen envelope and dependency/currentness checks, under the shared byte budget. |
| `request-decision-router` | Consume resolved request context; retain deterministic route, consequence, and effect boundaries. |
| `codex-app-server-wrapper` | Prepare interpretation before final route commitment; bind state, expectations, and lesson applications to the turn; join completion and delayed feedback; checkpoint updates before acknowledging them. Optional background learning never delays forwarding an already completed user result. |
| `evolution-runtime` | Own progress-to-target/hypothesis adapters and use existing research, observation, experiment, scheduler, and variant APIs. The durable trigger adapter uses the existing reasoning ledger. |
| `real-reasoning-v1` | Own fixed corpora, comparators, gain/protected checks, and per-run reporting. Do not auto-promote an inferred personal preference into a global engine rule. |

Prototype operations: `reduceInteractionState(previous, event)`,
`assessGrounding(input)`, `materializeCommunicationPreference(input)`,
`assessPreferenceApplication(preference, request, policy)`, and
`projectInteractionContext(state, request, policy)`. Add
`assessInteractionOutcome(turn, observations, policy)`,
`assessLessonApplication(input)`, and `composeInteractionLearningLoop(input)`
in the intent owner; add `assessInteractionLearningProgress(input)` and
`projectInteractionLearningToHypothesis(input)` at the evolution boundary.
Freeze exact input/result shapes during interface prototypes and continue
implementation without an intermediate approval request unless evidence exposes
a material change to this scope.

### Turn ordering

```text
raw request + recovered state + current user controls
  -> verify selected interaction dependencies and scope
  -> deterministic reference/focus projection + provisional route
  -> if material ambiguity remains: bounded optional interpretation or ask
  -> final request interpretation and route selection
  -> required definitions + ontology lock + interaction item selection
  -> one frozen Context Envelope and final Intent Contract
  -> Codex dispatch
  -> completion observation and coverage-aware outcome assessment
  -> attributed correction / scoped reflection / append-only state update
  -> later lesson application and observed benefit or counterevidence
  -> progress assessment -> retain / revise / bounded research and experiment
```

1. Keep a cheap route before full Context Basis construction, as the existing
   product rule requires. It is provisional where interpretation is unresolved;
   no route-owned work starts before final current context is available.
2. Resolve clear references from verified state without a mandatory extra model
   call. Give any optional interpreter actual bounded meanings, raw request,
   source spans, roles, focus, and unresolved alternatives—not digest-only input.
3. If interpretation needs additional definitions, select only those needed.
   Permit at most one interpretation-driven route refinement in this vertical;
   rebuild affected context and ask if a material conflict still remains.
4. Distinguish “a reference is unclear” from “a decision needs the owner.” If a
   requested read-only prerequisite can supply the missing information, perform
   it under the appropriate route before asking an avoidable question. Do not
   perform either of two materially different implementation choices by guess.
5. Bind the final contract to the envelope containing the selected interaction
   items. Avoid a digest cycle: the interaction projection does not embed the
   final contract; the final contract references the completed envelope.
6. Seal the turn's selected state and policy. A delayed extractor result cannot
   modify that turn or apply across a newer correction without reassessment.
   Replay reconstructs products without calling a model.
7. Append application/outcome/feedback events using exact turn, lesson revision,
   source-event, and assessment identities. Duplicate delivery produces the same
   records and does not increment learning counts. A correction to an earlier
   turn creates a linked successor, not a rewritten completed frontier.
8. The optional background evolution path receives a durable trigger only after
   attribution, retention policy, and scope checks. Unknown external delivery
   after a crash stops that trigger, not independent user work. No automatic
   successor action may bypass existing continuation and effect checks.

Use the wrapper's existing supported context/provider interfaces. New diagnostic
fields belong in ARE's own versioned fragments, not invented Codex protocol
fields. Expose explicit interpretation products, never a model's hidden
chain-of-thought, and never require internal labels in ordinary user output.

### Scope, control, integrity, and speed

- Separate visibility (`quiet/explain/inspect/control`), retention, and learning
  mode (`off/observe/apply-scoped`). Quiet presentation does not imply hidden
  learning permission. Existing configurations keep existing behavior until the
  new capability is explicitly enabled; new preference learning defaults to
  `observe` within the current interaction.
- Current explicit instructions remain instructions even when learning is off.
  Inferred preferences never override them or higher-priority requirements.
  Do not turn a soft preference into a hard constraint without supporting text.
- Bind identity to an authenticated participant/owner context, not a bare
  `consumer_id`. V1 supports current-interaction and explicitly selected
  current-product scope; cross-product/account-wide inference is deferred.
- Preserve source roles and exact spans. Retrieved text, quoted examples, tool
  output, and agent agreement are not user preference instructions. Do not infer
  sensitive traits or a general personality profile from writing style.
- A correction can produce a candidate with alternatives and counterevidence.
  “Confirmed” requires attributable evidence about that interpretation, not
  merely well-formed JSON or a high model score.
- Reuse only current selected dependencies. A relevant correction, policy
  revision, participant change, or referent-source drift requires reassessment;
  unrelated drift remains diagnostic. Interaction-bound views still receive
  successor identities even when reusable selected content bytes are unchanged.
- Share the existing inline budget (default 32 KiB) with all context fragments.
  Reserve mandatory material first; record optional exclusions. Block if
  mandatory context cannot fit. Do not silently truncate or generatively rewrite
  retained source meaning to meet a budget.
- Keep stable configuration and unchanged selected-state content separate from
  volatile turn identity/currentness receipts. Measure actual outgoing prefix
  bytes; append-only storage alone does not establish prompt cache reuse.
- User controls must support inspection, correction, rejection, scope changes,
  and disabling future reuse. “Forget” must distinguish disabling reuse from
  physical deletion of retained source bytes; an invalidation event is not an
  erasure implementation.
- Extend the existing `cyberalchemy/intent/get`, `project`, and `control`
  surfaces to show the loop and control lesson scope, application, and research
  contribution. Check authenticated ownership and the expected current revision
  before an update; checkpoint a successful update before its acknowledgement.
  Quiet mode still exposes blockers and consequential decisions. Deep inspection
  answers what was inferred, why it was retained, where it was applied, and what
  evidence supports its effect.
- Recovery must restore scope, exclusions, supersession, disabled state, and
  evidence—not only favorable conclusions. Reuse must not cause duplicate
  observation, correction, or model dispatch events after reconnect.
- Preferences and interpretation can constrain presentation and clarify intent.
  They cannot grant action authority, remove an obligation, or turn an
  opportunity marker into a causal marker.

Use successor record versions for meaning-changing contract changes. Keep
historical v1 records and receipt bytes readable and unchanged; require explicit
compatibility adapters where needed, not implicit reinterpretation on replay.

## 5. Construction DAG

```mermaid
flowchart TD
    A["A · Capture current baseline and scoped source closure"]
    D["D · Define pack and source bindings"]
    M["M · Product / ontology / DomainSpec / interface prototypes"]
    B["B · Freeze benchmark episodes, variants, scoring"]
    R["R · Deterministic state and bounded projection"]
    L["L · Grounding, scoped lessons, user controls"]
    F["F · Outcome checks and later lesson-application evidence"]
    I["I · Preflight, completion, and feedback integration"]
    P["P · Append-only persistence and recovery"]
    E["E · Progress triggers and existing evolution pipeline"]
    T["T · Complete-loop canary and four-variant benchmark"]
    V["V · Full regressions and real Codex canary"]
    C["C · Exact product candidate and test report"]
    O["O · Owner product review"]
    A --> D --> M
    D --> B
    M --> R
    M --> L
    M --> F
    R --> I
    L --> I
    F --> I
    R --> P
    L --> P
    F --> P
    F --> E
    B --> E
    B --> T
    I --> T
    P --> T
    E --> T
    T --> V --> C --> O
```

This describes parallelizable work, not authorization to spawn helpers. Freeze
shared interface shapes at M; assign disjoint new modules to R/L and keep one
owner for shared contract exports and wrapper integration. F can proceed from
the same frozen interface fixture. E uses those outcome fixtures while I/P join
the serving path; T proves the actual joined loop rather than separate demos.

| Node | Owner / deliverable | Completion evidence |
| --- | --- | --- |
| A | Implementation owner: current tests, exact scoped files, and existing source/profile bindings. | Baseline failures and active-owner overlaps are recorded causally; do not overwrite dirty files or relabel historical acceptance. |
| D | ARE meaning owner, using Define: seven record definitions, scoped Reflection extension, workflow, and reused evolution meanings. | Every concept has one disposition, exact sources, boundaries, examples, counterexamples, and named consumers. Present the generated meanings and continue within approved scope. |
| M | ARE model/interface owner: first-class capability contract and the product, business, DomainSpec, compiled-system, and interface prototypes. | Required inputs/outputs/relationships trace to D; exact affected generated projections replay deterministically. |
| B | Benchmark owner: frozen corpus, four variants, independent scoring, model/environment manifest. | Fixtures cover known failures and counterexamples without leaking expected answers into treatment input. |
| R | Intent/context owner: pure state reduction, application selection, stable projection, currentness. | Determinism, budget, dependency drift, immutability, and no-op tests. |
| L | Intent/control owner: source-bound grounding, scoped lessons/preferences, inspection and control. | Immediate repair remains independent of retained learning; no unauthorized scope expansion, source laundering, or inferred hard constraints. |
| F | Intent/outcome owner: expectation checks, feedback attribution, and lesson-application assessments. | Missing evidence is inconclusive; dispatched is not satisfied; delayed corrections and counterexamples create attributable successors. |
| I | Wrapper owner: revised preflight ordering, completion evidence, feedback hooks, and inline model inputs. | Mock Codex receives useful meanings; result and correction events close the loop; gated paths dispatch nothing; fast paths make no extraction call. |
| P | Reasoning-state owner: event/checkpoint/replay and trigger-outbox integration. | Restart restores identical state, disabled lessons, counts, and trigger identities; duplicate messages do not repeat lessons, experiments, or effects. Unknown delivery remains explicit. |
| E | Evolution owner: progress assessments, research triggers, hypotheses bound to implementation patterns, and measured experiment feedback. | Counterevidence revises the hypothesis; no-gain/budget bounds stop retries; missing providers are visible; serving version never switches. |
| T | Benchmark/validation owner: full correction-to-application-to-experiment cycle and paired comparisons. | Every run reports gains, regressions, cost, latency, coverage, stop reason, and failure examples; stored lessons alone cannot earn improvement credit. |
| V | Validation owner: all relevant ARE suites, compatibility/replay checks, controlled real app-server canary. | Exact runtime and model versions plus current evidence; missing real canary is reported as not run, not PASS. |
| C | ARE candidate owner: one transitive changed-source closure and current product-test report. | Test evidence binds the exact candidate; later source changes require a new test epoch. |
| O | Product owner: review the tested product. | Explicit product decision only; admission, activation, release, deployment, and other effects stay separate. |

### Current frontier and operational support

- **Product-construction frontier:** the closed-loop design and scoped baseline
  are ready for implementation approval. A then D are the next runnable tasks.
  Fixture outlines can be drafted alongside the source audit; executable
  assertions wait for D/M's settled meanings. Baseline issues unrelated to these
  prototypes remain visible and do not block them.
- **Causal construction dependencies:** typed reference scope, grounding
  evidence, view-versus-Context identity, and preference applicability must be
  specified before R/L/F can share a stable interface. I also depends on the
  completed-envelope/final-contract digest ordering; E depends on observable
  outcome and comparator identities, not a model's untested causal explanation.
- **Operational support — repository/worktree owner:** preserve and reconcile
  the in-progress product relocation before staging overlapping changes.
  Affected stage: shared-file integration, not definition or fixture drafting.
  Commit/push work is not part of this plan.
- **Operational support — benchmark owner:** pin external corpus revisions and
  check licenses before copying data. Affected stage: external benchmark import
  only; locally authored fixtures remain runnable.
- **Operational support — runtime owner:** verify the already configured exact
  model/binary against the test profile and apply section 9's live-call limits.
  No silent substitution or automatic state-database repair. Affected stage:
  real-provider test only; deterministic and mock tests do not wait for it.
- **Deferred operational residue:** cross-device/account-wide preferences,
  physical-erasure policy for retained logs, ACI integration, publication,
  admission, and deployment. None is a prerequisite for this scoped prototype.

## 6. Planned file changes

Repository-relative targets below are a future edit plan, not changes made now.
Before each implementation node, check local ownership and name its exact
allowlist; do not sweep an entire package into a commit.

| Node | Exact principal targets / intended effect |
| --- | --- |
| D | Add `cyberAlchemy-v2/development/agent-reasoning-engine/planning/interaction-context/DEFINITION-PACK.v1-candidate.json` using Define's existing materializer, with its required session/output records. Do not hand-edit the canonical definitions store. |
| M | Extend `cyberAlchemy-v2/development/agent-reasoning-engine/design/ARCHITECTURE.md`; reconcile `cyberAlchemy-v2/agent-reasoning-engine/product-capability.json`, `product-capability-support.json`, `business-ontology.json`, `bridge.json`, `sources.json`, and `residue.jsonl`. Add the child capability contract at proposed `cyberAlchemy-v2/agent-reasoning-engine/capabilities/interaction-context/product-capability.json`, registered explicitly with the owning product. Bind the exact DomainSpec nodes, schema, and builder/validator outputs before editing them. |
| R/L/F | Add `interaction-state.mjs`, `interaction-context.mjs`, `grounding.mjs`, `preferences.mjs`, `lesson-application.mjs`, and `learning-loop.mjs` under `cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/request-intent-runtime/src/`; narrowly extend `contracts.mjs`, `compiler.mjs`, `reflection.mjs`, `inspection.mjs`, and `index.mjs` exports with compatibility tests. |
| I | Extend `cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/codex-app-server-wrapper/src/intent-lifecycle.mjs`, `wrapper.mjs`, `continuation.mjs`, `config.mjs`, `preflight.mjs`, and `evolution-signals.mjs`; add `src/interaction-learning-lifecycle.mjs` and dedicated `profiles/interaction-learning-canary-v1.json`. Existing serving profiles stay disabled/unchanged. |
| R/I | Extend `cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/context-basis-runtime/src/context-envelope.mjs` and `context-refresh.mjs` only for typed interaction items, shared byte accounting, and selected-dependency checks. Include their focused tests; do not change unrelated compaction policy. |
| P | Reuse `packages/reasoning-state-runtime/index.mjs` append/checkpoint/frontier/replay APIs; place loop replay and durable trigger bindings in the new wrapper lifecycle module and `packages/evolution-runtime/src/interaction-learning.mjs`. Change the generic ledger only if its exact contract requires it, with focused compatibility evidence. |
| E | Add `cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/evolution-runtime/src/interaction-learning.mjs` and its tests; extend existing evolution exports/record verification as required. Reuse `src/scheduler.mjs`, the hypothesis/experiment APIs, and the existing gain-gated comparator. Do not replace the scheduler or upgrade controller. |
| B/T | Add `cyberAlchemy-v2/implementation/agent-reasoning-engine/benchmarks/real-reasoning-v1/src/interaction-context.mjs`, `src/interaction-learning.mjs`, `bin/interaction-learning.mjs`, `corpus/interaction-learning.jsonl`, and their tests. Extend `profile.json` and `src/corpus.mjs` through a new benchmark identity; freeze exact run manifests under this plan. Preserve prior intent and continuation benchmark identities. |
| C | Add the exact changed-source manifest and product-test report alongside this plan; update the first-class ARE README/scorecard with measured results, not proposed scores. |

The child capability's registry shape is an M interface-prototype decision. Its
first-class status must come from explicit product registration and contracts,
not merely from creating a directory. Do not manufacture missing support in a
validator by relaxing validation.

## 7. Benchmark plan

### Small local benchmark first

Start with **48 multi-turn episodes**, split by independent scenario lineage
into 24 development, 12 regression, and 12 holdout episodes. Paraphrases and
continuations of the same episode stay in the same split. Existing chat examples
belong in development/regression, never in a supposedly unseen holdout.

Cover eight families: construction versus visible wording; referents/focus and
causal continuation; explicit and implicit preferences; context-dependent
non-applicability; override/reversal; correction versus changed mind; quoted or
injected non-user instructions; and visibility/retention/control behavior.
Add deterministic replay, budget, and recovery tests outside the scored corpus.

Freeze four variants before running:

| Variant | Input/treatment |
| --- | --- |
| V0 | Existing ARE intent/continuation path with the same available conversational evidence; no new interaction-state projection. |
| V1 | A generic preference-summary baseline from the same evidence under the same memory budget; charge any summary-generation calls and tokens. |
| V2 | Typed Interaction Context View with explicit preferences/reference bindings; inferred preference learning disabled. |
| V3 | V2 plus the complete scoped learning loop: correction/lesson formation, later application, observed outcome, and progress assessment. |

Give every variant the same evidence availability, tasks, model settings, tool
permissions, and total context budget. If using a history-limited condition,
apply the same limitation to every variant and report it separately. Keep answer
labels, judge explanations, and held-out corrections out of model inputs.
Counterbalance run order; record binary/model identity, provider configuration,
code/corpus digests, timing protocol, request count, and token/cost limits before
live execution. Do not select an exact model name from an unsupported alias.

Every learning episode contains a source request, result/correction opportunity,
later applicable request, and an out-of-scope or reversal counterexample. Feedback
is a timestamped input supplied only at the corresponding episode step, never
an answer key injected early. Pin scripted feedback identically across variants;
report adaptive human feedback separately rather than quietly changing the
experimental treatment.

Add transition tests for no correction, uncertain attribution, no observation,
repeated failure, stale lesson, revocation, no gain, exhausted budget, missing
research provider, malformed evidence, and out-of-order/duplicate completion.
Exercise `off`, `observe`, and `apply-scoped` independently of display mode.

### Checks and measurements

- Hard structural/safety checks: zero false authority grants, wrong-participant
  reuse, quoted-text preference admission, or mandatory-context truncation;
  preserve v1 replay and default-disabled behavior.
- Behavior: intent/target accuracy, correct continuation, preference adherence
  when applicable, false carryover when inapplicable, avoidable questions,
  repeated corrections, task correctness, and user edit/repair effort.
- Separate preference extraction, applicability, projection, and actual output
  compliance. An application receipt alone does not earn an adherence score.
- Report outcome-check coverage, eligible versus unevaluable applications,
  correction-to-repair success, recurrence after application, correct lesson
  rejection, and research-trigger precision. Do not mix incomparable cohorts.
  Freeze `episode_success_rate` as the primary local behavior metric, with a
  minimum useful gain of one additional successful episode in the fixed cohort;
  safety and wrong-scope application permit zero regression. For latency-target
  experiments, keep the existing gain-gated metric/delta separately declared.
- Score quiet-mode helpfulness without rewarding visible preference mentions or
  internal metadata. Use deterministic expectations for structural cases and a
  blinded rubric plus sampled human review for semantic cases; do not let the
  treatment judge itself.
- Initial performance targets on the measured host: existing routing p95
  at most 2 ms over 10,000 warm iterations; added deterministic interaction
  selection/projection p95 at most 10 ms for the declared bounded active set;
  full warm preflight/envelope projection p95 at most 250 ms. Use 50 active
  optional records plus declared mandatory context within 32 KiB; record the
  exact fixture, warmup, and timing boundary with B. Report extractor/provider latency,
  model calls, tokens, and end-to-end response latency separately—none is claimed
  to fit inside the 2 ms router target.
- Measure exact outgoing prefix reuse and reused bytes from actual requests;
  report provider cache state as unknown unless observed. Cache hits do not
  establish currentness or semantic accuracy.
- Require all protected regression/safety checks and performance targets to
  pass. Report paired holdout differences and uncertainty; 12 holdout episodes
  are a smoke test, not enough to claim a general personalization improvement.
  A baseline at ceiling produces `gain-inconclusive`, not an invented gain or an
  endlessly rewritten benchmark. Define a larger follow-up before making a
  general claim; do not require statistical superiority to report functional
  loop implementation as complete.

Every experiment result must show a compact V0/V1/V2/V3 comparison, errors,
latency/cost, remaining failures, and the next hypothesis. A failure produces a
recorded hypothesis or stop decision, not endless retries under the same claim.

### Controlled scenario

Reproduce the reported “open the page, then plan and implement the next step”
case with three counterexamples:

1. One current ready causal step and an optional alternative: resolve the step;
   preserve the requested page read before dependent work.
2. Two genuinely different unresolved implementation choices: inspect the
   requested page if that is independently supported; then ask if the choice
   remains material. Do not manufacture a dependency to avoid asking.
3. A stale causal marker or changed objective: invalidate the old selection and
   reassess instead of continuing from familiar wording.

Then add “do not put these labels in the UI,” a later unrelated writing task,
an explicit preference reversal, and a reconnect. Check that the system learns
the scoped correction, avoids literal label leakage, does not overgeneralize,
and recovers the same controlled state.

The end-to-end mock canary must continue beyond saving the lesson:

```text
misinterpretation -> correction -> scoped lesson
  -> applicable reuse -> attributable supported/contradicted outcome
  -> recurrence or no-gain trigger -> exact hypothesis and code-pattern target
  -> declared research provider -> baseline/treatment experiment
  -> comparison and Learning Decision -> retained negative or positive evidence
  -> restart -> identical state/counts and no duplicate trigger
```

Cover both improvement and rejection branches using declared fixture providers;
label their research/experiment output as fixture evidence. Include a genuine
local runtime baseline/treatment benchmark separately. Neither a fabricated
provider result nor a successful state-machine transition establishes efficacy.

## 8. Selected evidence and refresh boundary

Audit date: 2026-09-04. These hashes identify inspected local source bytes; they
are not acceptance bindings and require no human byte confirmation.

| Source | SHA-256 |
| --- | --- |
| `packages/request-intent-runtime/src/contracts.mjs` under the implementation root | `46639a9898b9e4d90db883c7c46418390e81067cfe98f87f4870a6215cb482b6` |
| `packages/request-intent-runtime/src/compiler.mjs` | `99c30c49f3172170ca38c0dd29fc895da63a3f383bf1f988be3ced018a6c9809` |
| `packages/request-intent-runtime/src/reflection.mjs` | `69b5af5b01ee22a4abf7acfc06336922aa5b075e6dc0eeb0c77b437b4cfc93ca` |
| `packages/codex-app-server-wrapper/src/intent-lifecycle.mjs` | `08b5a3ccc059a2a38bf75d9ae1885d44c8010515d9e5bcd9f962bc639128795b` |
| `packages/codex-app-server-wrapper/src/wrapper.mjs` | `e5aca5fdb6870f197fe9404f63f1b7dc993e22d1cd9220d08c9e4fa67d47ee2d` |
| `packages/codex-app-server-wrapper/src/continuation.mjs` | `2f8d113a2a4dba3c7195e987169342caa292b3384ff5759bbd0f7869e10670a7` |
| `packages/codex-app-server-wrapper/src/evolution-signals.mjs` | `7a9ebae3b214d4ad3c940800111212903b87679a0fba8fd626af37e87b4bcdb7` |
| `packages/evolution-runtime/index.mjs` | `87836337ba3c3cc30ea536ff25d7712bc53d266f50e8259ec28196bad734bfbc` |
| `packages/evolution-runtime/src/scheduler.mjs` | `d9d477f1194a2e6e81cebf9fd2063bb76e408c25e5a22d3a9c0c756c9212f8b8` |
| `benchmarks/real-reasoning-v1/src/scorer-loop.mjs` | `b82aca16038c54ba3827b8a15cbdff27d01237bd688b49fbbe8911038605681f` |
| `development/agent-reasoning-engine/design/ARCHITECTURE.md` under CyberAlchemy-v2 | `1958758a104c19af9966fd1460097c18fbf919e480da45e5c8dcc0b5f4ffe0de` |
| `development/agent-reasoning-engine/CONTEXT-BASIS-DEFINITION-PACK.v1-candidate.json` | `9218a2181edbab2ebc99cda80f1b26760a8b0e4548acc871a6bcff806ba7e061` |
| `define/docs/DEFINITION-PACK.md` | `d52378ceb47691a2a854ef23a32f319e1536c82113861fac9e32b1c3f1bcd609` |

Canonical meaning selectors are CAV2-D39, D65, D66, and D67 in
`cyberAlchemy-v2/authority/definitions/DEFINITIONS.md`. Ontology dependencies are
the following exact nodes of
`cyberAlchemy-v2/agent-reasoning-engine/business-ontology.json`:

```text
CA2-ARE-ACTOR-INTENT-OWNER
CA2-ARE-CONCEPT-CONTEXT-ITEM
CA2-ARE-CONCEPT-CONTEXT-ENVELOPE
CA2-ARE-CONCEPT-REQUEST-CONTEXT
CA2-ARE-CONCEPT-CONTEXT-WINDOW-VIEW
CA2-ARE-CONCEPT-CONTINUATION-DECISION
CA2-ARE-CONCEPT-REASONING-STATE-FRONTIER
CA2-ARE-RULE-ROUTE-BEFORE-BASIS
```

Selected-node digest:
`8e088706d2e5cf415a40221a078b6dea4c01ed9a86cd33a5cbdc8df76bfa227f`.
Method: select exactly these nodes, sort by ID, recursively sort object keys,
serialize compact JSON without a trailing newline, then SHA-256. No existing
ontology edge records are dependencies of this planning audit. New edges above
are proposals only. Ambient ontology drift is diagnostic; changed or missing
selected meanings require rechecking the dependent design. Do not run the
suspended Python ontology runtime as an admission or routing prerequisite.

## 9. One-shot implementation proposal

**Approval scope:** implement nodes A through C, using this plan's defaults,
through a final product-test report. Present the generated definitions and
intermediate benchmark results while continuing; do not insert routine human
approval stops between definition, scaffold, implementation, and test stages.
Owner product review O is the terminal handoff, not an approval the implementer
can manufacture. This document records a proposal, not that approval.

### Deliverables

1. One Define-generated pack covering the operating loop, seven record
   definitions, scoped Reflection extension, and reused evolution meanings.
2. A registered ARE capability prototype, reconciled architecture and product
   model, and deterministic affected DomainSpec projections.
3. The working request/observation/correction/application/progress loop with
   default-disabled production integration and a fully enabled test profile.
4. Inline model context before final routing, correct completed-turn and delayed
   feedback attribution, user inspection/control, and append-only recovery.
5. A progress-to-evolution adapter that produces concrete hypotheses, exact
   implementation-pattern targets, bounded research/experiment work, and
   measured learning decisions using the existing runtime.
6. A reproducible runner with mock, local-benchmark, and live-canary modes;
   frozen inputs; explicit limits; and readable output after every experiment.
7. A complete result chain, negative outcomes included, plus one exact tested
   source manifest and final report. No production upgrade is part of the run.

### Test and execution budget

| Work | Bound and completion condition |
| --- | --- |
| Baseline and regression | Node v26.8.1; all ARE package suites, no skipped tests hidden as PASS. Preserve unrelated baseline failures as separate evidence while testing the changed closure. |
| Functional benchmark | 48 episodes × 4 variants, two deterministic replays; fixed dev/regression/holdout splits. Replay equality proves determinism, not independent empirical replication. |
| Progress/evolution experiments | At most three distinct hypotheses/attempts and one research cycle for the selected target. Reuse the gain-gated comparator; execute supporting, counterevidence, no-gain, and missing-provider branches. |
| Performance | 10,000 warm routing iterations; 50-record bounded selection/projection test; existing full preflight timing. Report environment and model work separately. No threshold relaxation after failure. |
| Recovery | Real file-backed checkpoint/restart in the mock suite; duplicate/out-of-order completion, correction, control, application, and research-trigger replay. Interrupt around trigger/sink boundaries and preserve delivery uncertainty. |
| Real Codex canary | Existing app-server proxy, exactly the model configured in the frozen benchmark profile, and a matching observed binary. One six-turn episode for each of four variants: at most 24 `turn/start` calls and 24 optional interpretation/reflection provider calls. No separate model-judge calls. Stop new dispatches after 30 minutes; report unfinished work and any in-flight call honestly. |
| Live canary effects | Scratch fixture artifacts only, within the test workspace; no user-project mutations by the canary, external messages, releases, credential changes, state-database repair, or serving-profile activation. Model usage is bounded by the calls above; token/monetary use is reported when available, not guessed. |
| Model or provider unavailable | Do not substitute a model, install software, repair Codex state, or invent success. Finish independent tests; report the exact unrun portion and prerequisite. A missing optional research provider does not block the local/mock loop. |

Freeze the six live turns at B: initial task, explicit correction/repair, later
applicable use, out-of-scope counterexample, explicit revision/revocation, and
post-reconnect continuation. Feed the same scripted feedback to every variant.
The live run is an integration smoke test, not enough data to demonstrate a
general market advantage or reliable causal efficacy.

Default external research is provider-configured and queue-only when absent.
The mock canary proves the whole research-to-experiment join with labeled
fixtures; the local benchmark measures actual runtime behavior. Live research
results must be reported separately if configured and actually executed.

### Definition of done and reporting

- **Implemented/tested:** the whole joined cycle runs, all new contract,
  recovery, control, and protected behavior tests pass, and the affected model
  projections are reproducible. Report full-suite baseline failures separately.
- **Measured gain:** report the preregistered baseline/treatment difference,
  coverage, protected checks, latency/calls/tokens, and uncertainty. Use
  `gain-observed`, `gain-inconclusive`, or `treatment-rejected` separately from
  implementation status. Do not promise gains in advance.
- **Live integration:** use `PASS`, `FAIL`, or `NOT_RUN` with the observed model
  and binary. Mock results do not substitute for a missing live canary.
- **Every experiment:** display variant/hypothesis, baseline, treatment, delta,
  protected regressions, latency/cost, result, and next action or stop reason.
- **Final handoff:** source manifest, definitions/model changes, command to
  reproduce, complete test summary, benchmark comparison, canary evidence, and
  remaining limitations. Ask for product review only after the tested candidate
  exists; no commit, push, acceptance, admission, or deployment is implied.

Stop the implementation run for a genuine destructive-action, credential,
privacy, active-writer conflict, or scope expansion that cannot be worked
around. Continue independent construction work when only an operational test
prerequisite is unavailable. Do not use Task Session, a Goal wrapper, raw-byte
confirmation prompts, a second scheduler, or unbounded self-modification.

## Open Questions

The following working decisions close the earlier planning gaps for V1. They
do not require another design interview; reopen one only if implementation
evidence contradicts it or requires a material change in scope.

| Question | V1 decision / remaining limitation |
| --- | --- |
| New view schema or existing view fields? | Use the defined typed Interaction Context View specialization inside the existing envelope; no second Context identity. |
| How much evidence is enough for grounding? | Exact explicit user correction can repair the current interpretation. Unique low-risk reference evidence can support an inferred binding. Conflicting/material alternatives remain unresolved; model confidence is never user agreement. |
| What does `observe` retain? | Retain candidates only in the current interaction's configured reasoning store; do not apply inferred lessons. File-backed replay follows the existing log's retention rules. `none` adds no lesson records, but does not erase source turns already retained by the host. |
| What does “forget” mean here? | Disable future reuse with a checkpointed exclusion/supersession event. Name the control `disable-reuse`, not physical deletion. Source-byte erasure remains a separate capability. |
| May learning generalize across products or users? | No. Current-product scope requires explicit user selection; cross-product and cross-user behavior is deferred. |
| How does the new capability register? | Add a typed child capability contract and explicit parent/support/source/bridge entries while preserving the existing parent. Necessary schema extensions are limited to this modeled relationship and require tests, never weakened validators. |
| Is live evaluation a new model-selection decision? | No. Bind the existing benchmark profile's configured model and compatible binary. Missing compatibility yields `NOT_RUN`, not substitution. |
| What remains beyond this run? | Large external-corpus validation, account-wide memory, physical erasure, production background scheduling, and serving-version adoption. None is required to test the scoped loop. |

Next action after implementation approval: execute A through C under
`ARE-INTERACTION-LEARNING-001`, reporting progress and results through the final
test handoff. Approval to implement is not a claim that the finished product
has already been approved.
