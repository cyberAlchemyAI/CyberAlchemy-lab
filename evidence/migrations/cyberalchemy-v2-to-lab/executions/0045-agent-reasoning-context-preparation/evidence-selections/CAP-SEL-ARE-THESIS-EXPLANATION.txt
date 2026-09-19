# Agent Reasoning Engine

The Agent Reasoning Engine is the private CyberAlchemy-v2 capability for both
governed reasoning and context management.

This directory is its first-class Product package. [`product.json`](product.json)
owns the Product identity, [`product-capability.json`](product-capability.json)
owns the Product Capability, [`business-ontology.json`](business-ontology.json)
owns product-local meaning, and [`domainspec/`](domainspec/) owns the authored
and deterministic system model. Research and historical decisions remain in
[`../development/agent-reasoning-engine/`](../development/agent-reasoning-engine/README.md);
runtime code remains in
[`../implementation/agent-reasoning-engine/`](../implementation/agent-reasoning-engine/README.md).

## Product thesis

> **ARE helps people and agents solve problems with continuity. It reuses the
> reasoning state that produced context, makes the current objective explicit,
> checks its interpretation against results, learns scoped lessons from feedback,
> and improves the engine through research and controlled benchmarks.**

Context is what the model receives now. Reusable reasoning state preserves the
understanding and evidence used to choose that context: what the user wants,
why an approach was selected, what happened, what remains unresolved, and what
can usefully carry forward. It is inspectable system state, not hidden model
chain-of-thought.

```text
Interpret -> route -> act -> observe -> assess
   ^                                     |
   |                                     v
Reuse state <- measure application <- scoped lesson
                                         |
                          recurring weakness / no gain
                                         v
                         hypothesis -> research -> experiment
                                                        |
                                                        v
                                                measured feedback
                                                        |
                                                        v
                                               next improvement cycle
```

The immediate objective is the result the user wants now, not the broader
project goal or a route label. A new request can continue, refine, replace or
interrupt active work, or begin another objective. Understanding is a testable
claim: compare an explicit interpretation and expected outcome with evidence,
then retain support, counterevidence or uncertainty.

A lesson is useful only within its scope. When a user approves a diagram style
and asks to reuse it, preserve that presentation pattern for similar requests;
do not repeat obsolete wording or impose it on unrelated answers. Users can
inspect the reason, narrow the scope, override the preference or revoke it.
One-off instructions do not silently become permanent memory.

The serving engine handles current work; the evolution engine investigates
weaknesses and benchmarks changes. A measured candidate and permission to upgrade
are separate. Improvements must preserve declared speed, quality, reliability
and safety checks; repeated no-gain results change or stop the experiment.

**Implementation boundary:** the state, context, intent and continuation pieces
exist, but general objective-transition classification and the complete
interaction-learning connection remain planned. Today, wrapper preflight runs
before optional intent compilation. The local scores below do not prove general
conversational understanding.

Read the [in-depth product explanation](REASONING-AND-LEARNING.md) for the loops,
objective transitions, evidence model, current code and benchmark questions.
The [product ontology](ONTOLOGY.md#understanding-and-learning-product-view) gives
the corresponding concept-to-relationship-to-concept view.

### Current benchmark scorecard

The thesis is tied to measured behavior, not only to an architectural promise.
The canonical machine-readable record is
[`benchmark-scorecard.json`](benchmark-scorecard.json); every displayed value
is checked against an exact benchmark result.

<!-- BEGIN BENCHMARK SCORECARD -->
| Surface | Measured score | Local latency | Status |
| --- | --- | --- | --- |
| Request and context | 100% route accuracy; 100% definition recall; 91.7% context precision | route p95 1.144 ms; selection p95 0.200 ms; preflight p95 7.309 ms | PASS |
| Intent compilation | 100% intent alignment | p95 0.077 ms | PASS |
| Lifecycle and failure safety | Lifecycle and fail-closed checks passed | not timed as a score | PASS |
| Adaptive reasoning-state reuse | 100% fact preservation; 100% intent fidelity; stale reuse 5 -> 0; exact reuse 2/2 | lifecycle p95 16.974 ms | PASS |
| Route continuation | 16/16 scenarios passed; 100% need recall; 100% completion precision; no premature stops or over-continuations | decision p95 1.873 ms; observed wrapper p95 459.682 ms | PASS |
| Adaptive reuse holdout | 8/8 scenarios passed; 100% fact preservation; 0 stale reuse incidents | lifecycle p95 14.263 ms | PASS |
| Compaction projection | 100% pinned-state survival; 100% recovery; 96.9% mean byte reduction | warm p95 0.0045 ms; cold p95 1.657 ms | PASS |
| Automatic compaction recall | 0% baseline -> 100% ARE exact recall across 5/5 compacted pairs | not measured in this experiment | PASS |
| Literal-versus-intent scorer | 66.7% -> 100% agreement; false negatives 57.1% -> 0%; false positives remain 0% | full-evidence p95 0.00143 -> 0.00651 ms | FAIL |
<!-- END BENCHMARK SCORECARD -->

The deterministic rows were rerun on Linux x64 with Node v26.8.1. The automatic
compaction row is the recorded five-pair `gpt-5.6-luna` app-server experiment.
The route-continuation treatment reconciles materialized candidates with an
explicit objective frontier, blocks missing candidate discovery, gates missing
human input or choices, and ignores stale proposals after objective completion.
The measured wrapper latency is a 16-scenario observation rather than a stable
latency guarantee.
The literal-versus-intent scorer improved quality but remains rejected because
it missed the latency gate. The full Agent Retrieval Bench release is still
unmeasured; only its structural fixture has run. These are local product
candidate scores, not a market-wide quality claim.

Its central context principle remains:

> **Do not merely reuse context. Reuse the explicit reasoning state that
> produced that context.**

Agent systems commonly preserve a transcript, a prompt, or a provider cache but
discard the causal and evidential structure used to assemble it. The next turn
must rediscover why definitions and ontology records were selected, which
sources were current, what was excluded, which contradictions or gaps remained,
and which continuation was still eligible. Identical prompt bytes can conceal a
different reasoning basis; different prompt bytes can contain a still-current
reasoning basis.

ARE makes that explicit reasoning basis a reusable system asset. It records and
seals provenance-bearing reasoning-state epochs, validates only their selected
dependencies, projects bounded Context Envelopes for consumers, binds explicit
semantic and continuation results, and creates successors only when relevant
state changes. This is not storage or exposure of hidden model chain-of-thought.
It is reuse of inspectable system records: request interpretation, route,
definitions, ontology selections, evidence posture, exclusions,
contradictions, gaps, transformations, freshness, admitted observations,
receipts, decisions, and the continuation frontier.

## Progressive inspectability and user control

ARE must preserve a complete structured account of how a request became an
action while letting each person choose how much of that account appears during
normal work. Inspectability and control are properties of the engine, not a
special diagnostic build or a permanently verbose interface.

The engine projects four views from the same reasoning state:

```text
quiet
  result, material assumptions, blockers, and consequential decisions

explain
  interpreted objective, concise rationale, selected route, and changes

inspect
  Intent Contract, Context Envelope, selected sources, referent bindings,
  transformations, exclusions, contradictions, events, and receipts

control
  correct intent, rebind a reference, reject an assumption, pause an action,
  choose retention scope, replay an epoch, or redirect continuation
```

Changing the view never changes the underlying reasoning-state epoch. Every
displayed explanation points to the records that support it, and deeper views
remain reachable from the ordinary interaction. The inspectable product is the
engine's structured rationale and provenance—not hidden model chain-of-thought.

The Intent Reflection Loop uses the same control model. When a user correction
reveals a likely misinterpretation, omitted constraint, wrong referent, unsafe
assumption, or realization defect, ARE records the before-and-after intent and
offers three independent choices:

1. repair the current result;
2. retain the correction for the current interaction or product; and
3. propose a benchmark case and engine-improvement opportunity.

ARE may perform the immediate repair without treating the correction as a
general rule. Cross-interaction retention, benchmark construction, and adoption
of an engine change remain separately visible and controllable. A person may
also reclassify an apparent reasoning failure as a new preference, a change of
mind, or environmental drift so the improvement loop does not learn the wrong
lesson.

This creates a user-visible path through the improvement cycle:

```text
request -> intent -> action -> correction -> reflection
        -> scoped lesson -> benchmark candidate -> measured improvement
```

The default can remain fast and restrained. Expert users can open the reasoning
frontier, inspect why context and routes were selected, alter controls, compare
epochs, and decide which lessons become durable inputs to engine evolution.

The product promise is that a person or agent can resume complex work from an
exact, reviewable reasoning frontier instead of reconstructing the work from a
conversation. Reuse preserves provenance, temporal scope, residue, claim
ceiling, and authority posture; it never upgrades them.

```text
request
  -> acquire or create reasoning-state epoch
  -> validate selected dependencies
  -> append changed evidence, judgments, and residue
  -> project consumer-specific Context Envelope
  -> reconstruct and dispatch the interaction
  -> bind explicit result and continuation records
  -> seal reusable successor frontier
```

The Context Envelope is therefore a projection of reasoning state, not the
primary durable asset. A model-provider cache is an optimization over exact
request bytes, not evidence that the underlying reasoning state is current.

## Research and evolution pipeline

The improvement loop follows one concrete pipeline:

1. Collect benchmark failures, slow paths, user corrections, unresolved gaps,
   and recovery failures.
2. Turn each recurring weakness into a measurable improvement target.
3. Search for papers, repositories, releases, tools, and techniques related to
   that target.
4. Record the exact source, version, mechanism, evidence, and limitations of
   each promising technique.
5. Reproduce the technique and determine where it fits in ARE.
6. Build one or more new engine versions.
7. Compare them with the current engine using fixed development, regression,
   holdout, performance, and failure tests.
8. Keep useful versions, discard regressions, and preserve the evidence from
   both.
9. Upgrade the serving engine when a version performs better.
10. Monitor the upgrade, roll it back when declared failures appear, and feed
    the new results into the next improvement cycle.

The evolution runtime now implements the complete bounded mechanism chain:
diagnosis signals, deterministic target selection, provider-neutral research,
technique and reproduction records, content-addressed isolated variant
workspaces, exact benchmark comparisons, recommend-only upgrade decisions,
atomic controlled-local serving selection, canary rollback, and one-cycle-at-a-
time scheduling. The real-reasoning benchmark includes a deterministic full
cycle canary. The mechanisms do not invent research sources or code changes:
production providers, reproduction protocols, mutation runners, schedules, and
activation remain explicit configuration.

The first three mechanisms are now bounded candidate implementations in
`implementation/agent-reasoning-engine/packages/reasoning-state-runtime` and
the Codex app-server wrapper: an append-only Reasoning State Ledger, required
risk-aligned checkpoints, and exact outbound request reconstruction. The
direct wrapper default is process-memory; the persistent gateway derives one
append-only JSONL plus `fsync` log per declared consumer. The successor recovery vertical now verifies a
complete log, rebuilds disposable indexes, selects its final checkpoint, and
continues the exact event chain before Codex accepts a new turn. An atomic
single-writer lock prevents concurrent mutation and clean shutdown releases it;
stale-lock adjudication, repair, physical compaction, automatic reduction or
import policy, and durable CyberAlchemy Session semantics remain open, so this
is not yet the complete product promise.

The advanced reusable-state vertical now provides content-addressed branches,
exact replay-derived fixtures, append-only non-destructive reductions,
risk-scaled checkpoint selection, currentness-bound counterevidence, portable
epochs under exact compatibility, and provenance comparison that explains why
two apparently similar requests cannot reuse state. These are explicit opt-in
operations; no model autonomously summarizes, compacts, imports, or promotes
the resulting state.

The lifecycle coordinator now turns those primitives into one deterministic
transition contract: assess, plan, explicitly execute, and verify `reuse`,
`branch`, `reduce`, `checkpoint`, or `portable-export`, otherwise block. The
real-reasoning improvement loop is its first consumer. Benchmark baselines and
candidate closures are exact-bound, authority posture is measured from
failure-safety observations, outside-allowlist drift rejects the candidate,
and stability requires two observations of the same candidate digest.

The cache-affinity vertical projects a canonical stable request header and the
reusable explicit reasoning state before the volatile current-turn suffix. It
measures exact/common reused bytes, estimated reusable tokens, projection time,
and invalidation reasons. Provider cache hits and actual savings remain
unobserved and can never substitute for dependency currentness or provenance.

The completed-turn frontier vertical now seals the explicit semantic result,
continuation result, completion identity, and context bindings into the same
recoverable Reasoning State source before automatic continuation. After a
restart, the wrapper can replay that exact decision without rediscovering it or
starting a second successor. Delivery acknowledgement remains a separate gap,
so recovery uses an explicit at-most-once posture rather than guessing.

The completed-turn frontier vertical now seals the explicit semantic result,
continuation result, completion identity, and context bindings into the same
recoverable Reasoning State source before automatic continuation. After a
restart, the wrapper can replay that exact decision without rediscovering it or
starting a second successor. Delivery acknowledgement remains a separate gap,
so recovery uses an explicit at-most-once posture rather than guessing.

Its first-class candidate construction package is this directory. The package
separates:

- product meaning and business rules;
- DomainSpec-v2-authored system structure;
- deterministic graph and system-ontology projections;
- evidence-backed links to bounded partial implementations, including the
  request-decision router, Context Basis lifecycle, production-shaped semantic
  input materialization, receipt-constrained continuation, bounded runtime
  journal replay, and a persistent Codex app-server gateway candidate;
- explicit gaps for production semantic activation and catalog adoption,
  general host adoption,
  durable cross-session context, whole-engine integration,
  implementation binding, conformance, and runtime evidence.

The engine manages what a bounded reasoning run may reason over, preserves why
that context was selected, derives a typed semantic result under frozen inputs,
and records when changed context invalidates reuse. It does not grant authority,
approve an effect, or replace CyberAlchemy-v2 routing and governance owners.

## Current posture

This is a private first-class Product candidate, not yet an approved or
canonically adopted Product. The semantic-judgment evaluator,
intent-route resolver, request-decision router, Context Basis lifecycle, and
Codex app-server wrapper are bounded local realizations. The context lifecycle
preserves usable selected meanings, creates immutable budgeted envelopes,
distinguishes selected-dependency invalidation from unrelated diagnostic drift,
and refreshes live sources before each wrapped Codex turn. It keeps plan-bound
reuse and interaction-bound succession distinct.

The semantic evaluator now has a bounded additive integration with the frozen
Context Envelope. It verifies the envelope and Context Items, derives a sealed
context-bound Problem Frame, verifies exact agreement among that frame, its
entry gate, authority snapshot, Context Envelope binding, selected Context Item
digests, freshness, and claim ceiling, then evaluates under the existing finite
catalog. Context-bound receipts preserve the context epoch, envelope, binding,
and selected-item identities; historical unbound receipt bytes remain unchanged.

The separate semantic-input runtime now selects exactly one configured semantic
domain, reloads exact-bound authority, catalog, and validator providers, admits
only source-and-validator-bound observations, freezes challenge and journal
state, and emits a sealed evaluator request. Missing domains are explicitly
not applicable; ambiguity, stale providers, missing ownership, malformed
sources, and structural ineligibility block before evaluator execution.

The Codex wrapper can now invoke that lifecycle at `turn/completed`, but only
through an exact opt-in semantic profile and explicit input provider. It binds
preflight context to the actual turn identity, emits compact outcome and receipt
metadata, and evaluates once per immutable turn. The repository default is
disabled and therefore performs no semantic provider or evaluator calls.

The wrapper can also emit immutable Improvement Signals at `turn/completed`.
This path is separately opt-in and requires both an explicit signal provider
and sink. Disabled mode makes zero calls. Completion-frontier replay prevents a
duplicate completion from emitting the same signal twice, and the diagnostic
journal stores only signal identities and counts rather than turn contents.

For plan-bound proposals that explicitly declare a semantic dependency, the
wrapper verifies the exact Reasoning Receipt, turn, Context Envelope,
materialization, domain, and terminal-outcome binding before deriving a
non-authorizing constraint. A recommendation remains advisory and cannot
override consequence, protected-effect, reversibility, or human-interaction
gates. Duplicate completions replay one verified immutable journal cut without
calling providers or evaluators or starting a second successor.

The separate completion journal is bounded in-memory state with hash-chained compact events,
immutable cuts, deterministic replay, idempotency, and closed-turn-only
eviction. The Reasoning State Ledger can now recover its own checkpointed file,
but that does not make the completion journal durable. No production
semantic-domain catalog or default activation is adopted, and there is no
cross-process or cross-session journal. The complete engine is not admitted,
published, or deployed.

The persistent gateway now separates transport from the reasoning wrapper. It
supports direct stdio, the official managed-daemon proxy, and an isolated
loopback WebSocket app-server backend. Declared plan and human/chat consumers
receive separate wrapper instances, upstream connections, and collision-resistant
per-consumer reasoning logs; reconnect retains the same live session, while a
clean process restart recovers checkpointed reasoning epochs and completion
frontiers. Lane substitution, concurrent attachment, and a second writer for
one log fail closed. The repository does not install or start a managed
daemon and does not modify Codex Desktop configuration.

Historical specifications, decisions, promotion receipts, and implementation
evidence keep their original claim ceilings. The new ontology does not rewrite
or widen them.

## Open Questions

See [the reasoning and learning explanation](REASONING-AND-LEARNING.md#open-questions)
for objective-classification, outcome evidence and retention questions, and
[`residue.jsonl`](residue.jsonl) for source reconciliation and implementation gaps.
