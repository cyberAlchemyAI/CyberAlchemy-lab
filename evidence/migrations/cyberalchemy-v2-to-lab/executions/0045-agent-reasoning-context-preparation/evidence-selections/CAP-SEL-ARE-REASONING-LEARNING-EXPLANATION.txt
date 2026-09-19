# Understanding, objectives and reusable reasoning state

This explains ARE's product model in depth. The ontology's product-local meanings
live in [business-ontology.json](business-ontology.json); the readable relationship
view is in [ONTOLOGY.md](ONTOLOGY.md#understanding-and-learning-product-view).
The current implementation boundary is explicit below. This document does not
define new runtime record schemas or a second memory/research service.

## 1. The problem and the product promise

A transcript can preserve every message while losing the useful structure of
the work: what the user meant, which result is still wanted, why a tool was
selected, what evidence supported a decision and whether a correction still
applies. Summarizing more text does not by itself recover that structure.

ARE makes the explicit reasoning state reusable. It selects the relevant,
current parts of that state to assemble context, preserves evidence for its
interpretation, and learns from attributable outcomes. It improves the engine
through experiments rather than treating familiar responses or confident
self-descriptions as progress.

## 2. Three connected loops

```text
Request + selected reusable state
                  |
                  v
Interpret -> identify objective -> route -> assemble context
                                               |
                                               v
                                      check permission -> act
                                                           |
                                                           v
                                                        observe
                                                           |
                                                           v
                                                         assess
                                                           |
                                  continue / ask / finish <-+
                                      |
                          next permitted step, if any
                                      |
                                      v
                           next request + current state

Assessment + attributable user feedback
                  |
                  v
Reflect -> scoped lesson -> apply when relevant -> measure application
                  ^                                      |
                  +--------- revise / suspend ------------+
                                                         |
                                                         v
                                               reusable reasoning state

Recurring weakness / no gain / explicit improvement request
                  |
                  v
Hypothesis -> research -> experiment -> compare with baseline
                                               |
                                               v
                                   retain / revise / reject
                                               |
                                               v
                                       measured feedback
                                               |
                                               v
                                   next improvement cycle
```

The first loop handles work. The second improves the interpretation or behavior
used on later work. The third tests changes to the engine itself. A retained
lesson is not a code upgrade; a successful experiment is not permission to deploy.

Route selection still precedes route-specific definition/ontology assembly and
strategy execution. Interpretation can use a small, already selected state
projection before committing that route; it does not require searching the whole
ontology or constructing the full route-specific context first.

Permission checks apply to each exact action. Completion assessment can identify
a further permitted step, a real decision, missing input or finished work.
"Continue" is not a command to keep acting after completion or past a boundary.

## 3. What reusable reasoning state contains

| Part | What is retained | Why it matters |
| --- | --- | --- |
| Interpretation | Proposed meaning, referents, source request, assumptions and uncertainties | Avoid reconstructing "what did they mean?" from scratch. |
| Active work | Immediate objective, scope, completion condition and relation to broader or suspended work | Avoid confusing a side question with cancellation or a project goal with today's action. |
| Evidence | Selected sources, provenance, currentness and contradictions | Reuse only the basis that remains applicable. |
| Decisions and residue | Selected approach, observed result, unresolved questions and permitted next steps | Keep unfinished work visible without inventing permission. |
| Lessons and preferences | Scope, supporting feedback, expected benefit, application history and counterevidence | Adapt without imposing an inferred preference everywhere. |

These are explicit inspectable records, not hidden model chain-of-thought.
Reasoning State Ledger and Epoch already supply the intended storage and
identity mechanisms; the new product meanings do not establish another store.

```text
Reasoning state = understanding + basis + outcomes + unresolved work
                               |
                    select relevant/current items
                               v
Context Envelope = what this consumer receives for this request
```

Historical state remains historical. Selected evidence changes can require a
successor; unrelated drift should remain diagnostic. Stable projections can
improve cache affinity, but identical bytes cannot establish freshness,
correctness or authority. Compaction must preserve load-bearing constraints and
counterevidence, not merely compress wording.

## 4. How understanding becomes testable

The engine does not establish understanding by asking itself whether it
understands. It proposes an interpretation, declares observable expectations,
acts, and compares those expectations with attributable evidence.

```text
Interpretation -> expected outcome -> action -> observed outcome
       ^                                             |
       +--- revise <- supported / contradicted / unknown
```

For "show the engine as an arrow diagram and reuse this format":

- A diagram in the answer supports format compliance.
- An explicit request to reuse it supports a scoped presentation preference.
- Current source checks support the correctness of the described architecture.
- Later feedback can support usefulness to the user.
- Controlled comparisons can establish a broader improvement claim.

These are separate checks. A correct format does not prove correct content.
A test passing establishes its tested property, not the entire task. Silence
does not prove satisfaction. A schema validates structure, not interpretation.
A model's evaluation can be a labelled diagnostic proposal; repeating it does
not create independent evidence.

Assessment preserves which checks were applicable, which were observed, and
which remain unknown. Missing outcome evidence must not default to success.

## 5. What makes an objective current

The current objective is the immediate result sought now. It has a source,
scope, completion condition and relationship to other work. It is not simply
the last sentence, a router category, or the overall project aspiration.

| New request | Transition | State consequence |
| --- | --- | --- |
| "Continue implementing it." | Continue | Retain the established objective and resolve the unfinished next step. |
| "Also handle reconnects." | Refine | Revise scope and completion conditions; reassess newly introduced effects. |
| "Instead, explain the design." | Replace | Select explanation as immediate work and explicitly record what it supersedes. |
| "Before that, explain this term." | Interrupt | Answer the side question while retaining the suspended objective. |
| An unrelated request with a distinct result | New | Establish another objective without silently completing or deleting old work. |

Stopping work is an explicit lifecycle operation, not evidence that its result
was achieved. Resuming suspended work still requires current applicability and
permission. Explicit current instructions outweigh old inferred context; if
"do next" has one established permitted continuation, reuse it. Ask only when
materially different outcomes remain unresolved.

A minimal illustrative record, **not an implemented schema**, is:

```text
desired result: explain objective classification
source: current user question
relationship: interruption of implementation discussion
scope: explanation only
completion: explain selection, transitions and uncertainty
suspended work: prior implementation objective
```

Keep three existing representations distinct: an intent contract's objective
describes desired work; request-context objective_kind selects a routing
category; an objective frontier describes whether further work is runnable,
blocked, complete or needs input/choice. None alone is a general conversation
transition classifier.

## 6. Learning the user's approved explanation style

The user explicitly approved the compact arrow-loop explanation and requested
its reuse. Preserve the useful pattern: show causal sequence and feedback paths,
then explain the parts briefly. Do not memorize a diagram's old edges as forever
correct, render internal metadata into the product surface, or make every answer
a diagram.

```text
Explicit format approval + reuse request
                  |
                  v
Scoped preference with source and exclusions
                  |
                  v
Similar request -> apply pattern -> observe result
                                      |
                                      v
                         retain / narrow / override / revoke
```

A one-off formatting request is fulfilled now without inventing indefinite
retention. A later "prose only" instruction overrides the earlier preference.
Users can inspect what was learned, why, where it applies, and how to remove it.
The interface need not display that machinery in every ordinary answer.

The [approved-format example](../development/agent-reasoning-engine/planning/interaction-context/APPROVED-EXPLANATION-EXAMPLE.md)
contains the originating user statement and proposed test cases. Saving that
example is not proof of automatic runtime preference learning.

## 7. Current code versus the product model

Source inspection on 2026-09-05 found:

| Current code | What it does | Missing connection |
| --- | --- | --- |
| [Intent compiler](../implementation/agent-reasoning-engine/packages/request-intent-runtime/src/compiler.mjs) | Uses objective_hint or the first request sentence on its fast path; a configured provider can supply a structured candidate. | General transition classification from active/suspended work is not supplied by the fallback. |
| [Request context](../implementation/agent-reasoning-engine/packages/codex-app-server-wrapper/src/request-context.mjs) | Takes objective_kind from a context hint or turn binding, otherwise null. | A category is not a fully grounded objective. |
| [Intent lifecycle](../implementation/agent-reasoning-engine/packages/codex-app-server-wrapper/src/intent-lifecycle.mjs) | Opt-in compilation and correction handling; passes request, context digests and source references. | It does not pass the full selected objective/interaction meanings into the compiler. |
| [Continuation](../implementation/agent-reasoning-engine/packages/codex-app-server-wrapper/src/continuation.mjs) | Validates supplied causal/opportunity bindings, derives a frontier, and resolves a bounded set of short continuation phrases against a selected proposal. | Supplied relation labels and phrase matching do not classify arbitrary new requests. |
| [Wrapper](../implementation/agent-reasoning-engine/packages/codex-app-server-wrapper/src/wrapper.mjs) | Projects prior continuation, runs preflight, then optional intent compilation and dispatch. | Interpretation arrives too late to resolve a request preflight has already stopped. |

Thus the target integration is:

```text
request + selected active state
            -> interpretation + objective transition
            -> explicit current objective
            -> committed route + necessary context
            -> observed result + checked understanding
            -> scoped learning + measured application
```

The [implementation plan](../development/agent-reasoning-engine/planning/interaction-context/PLAN.md)
owns this unfinished integration. Existing scorecard results cover their exact
fixtures, not general discourse understanding. No benchmark score or runtime
behavior changes with this document.

## 8. How the claims should be benchmarked

Keep separate measures for objective selection, transition classification,
referent grounding, unnecessary clarification, premature stopping, excessive
continuation, and scope/effect violations. Include multi-turn interruptions and
return-to-work cases; isolated sentence labels cannot prove continuity.

For lessons, measure applicable reuse, inappropriate reuse, current-instruction
override, revocation after replay, outcome coverage and formatting corrections.
A selected lesson is not necessarily projected, dispatched, followed or useful:
record and test each boundary.

Compare baseline and treatment on held-out episodes using the same checks and
cost accounting. Never use a model's own preference diagnosis as both treatment
and sole judge. Track time and extra model calls, protected regressions and
minimum useful gain. No gain changes or stops the strategy; it is not a reason
to run the same experiment indefinitely.

## Construction frontier and operational residue

Product construction: the product-local meanings, ontology relationships and
this explanation are runnable design work. Implementation remains with the
existing interaction-learning plan; no parallel interpreter or memory service
is proposed here.

Operational support: the package validator reports pre-existing drift in
CAP-SEL-ARE-CODEX-WRAPPER and CAP-SEL-ARE-JOURNALED-CODEX-WRAPPER. Their owner must
reconcile those exact bindings before full deterministic system rematerialization.
No hashes for these unrelated runtime changes were silently refreshed. This
does not prevent authoring product meanings. Existing generated projections and
historical receipts remain historical, not evidence for the new relationships.

## Open Questions

- Which outcome checks distinguish successful objective completion from partial
  compliance for each supported request class?
- What scope and cross-conversation retention should the user explicitly control?
- Which held-out cases and minimum useful gains will validate the transition and
  lesson-application integration?
