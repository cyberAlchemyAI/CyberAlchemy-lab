# CyberAlchemy Product Thesis

Status: candidate
Canonical kind: product-thesis
Thesis ID: CA2-PRODUCT-THESIS-CYBERALCHEMY
Canonical definition: CAV2-D63
Commitment state: committed
Visibility: private
Meaning owner: CyberAlchemy v2
Authority effect: none

## Thesis

CyberAlchemy helps people and machines build and evolve complex systems
together through an ergonomic, governed work loop. It keeps intent, meaning,
evidence, decisions, action, feedback, and ownership connected. It shapes the
next move to fit the person, task, and moment while preserving domain priority,
owner boundaries, and human control.

In simpler language:

> CyberAlchemy helps a person and a machine notice what the work needs, choose
> the smallest useful governed action for the moment, and continue without
> losing meaning, evidence, ownership, or human control.

This is the product commitment CyberAlchemy is being built to realize. The
principles below are first-order product beliefs: they define what the product
must remain true to even before every interface or runtime exists. Evidence
determines whether a particular realization succeeds and which outcome, market,
or effectiveness claims may be made. It does not decide whether these principles
belong in the thesis.

This artifact is a candidate instance of the canonical `product-thesis` kind.
It is not Definition authority, promoted Spec authority, or a validated market
claim. The meaning of Product Thesis is owned by `CAV2-D63`; this document owns
the current CyberAlchemy thesis proposition.

## Why The Product Is Needed

Complex work is often split across chats, files, tools, agents, tests, and
people. A machine can produce an answer while the human still has to recover:

- which goal the answer serves;
- which meaning and evidence were used;
- which important questions were skipped;
- whether the next action is allowed;
- who must review or own it;
- what must remain usable in the next session.

The problem is not only missing automation. It is a disconnected work loop.
More automation can make that problem worse when it hides decisions or turns a
plausible answer into an apparently finished result.

## First-Order Product Principles

The product thesis commits to nine principles:

1. **Human agency** — important choices remain visible to the responsible
   person.
2. **Bounded and visible authority** — every consequential action shows who or
   what may make it real, which action and target are covered, and the scope,
   conditions, and lifecycle point of that authority.
3. **Governance serves the work** — the system carries routine checking and
   routing burden, while human-visible gates are concentrated where a real
   consequence changes.
4. **Dynamic human-machine work fit** — the product makes the right governed
   capability available at the right moment, in a form that fits the work, the
   person's explicit context and attention, and the evidence and ownership
   boundary.
5. **Shared meaning** — terms and relationships are made clear enough for the
   next stage to use them.
6. **Evidence continuity** — claims and decisions remain linked to their
   support and counterevidence.
7. **Owner continuity** — a recommendation or handoff does not become unowned
   output.
8. **Honest incompleteness** — missing knowledge stays visible instead of being
   hidden by a complete-looking artifact.
9. **Progressive context sufficiency** — use explicit intent context and
   references first, then provenance-marked current-window and saved-session
   context, and ask the person when that bounded evidence is still insufficient
   or indeterminate.

These are product commitments, not rewards granted after product proof.
Governance is useful only when it protects them while helping people and
machines understand, challenge, and continue the work.

## Projects, Goals, Research, And Experiments

CyberAlchemy connects this product thesis to concrete work through Projects and
Goals. A Project keeps related owners, evidence, decisions, artifacts, and work
under one stable identity. A Goal states one desired future result for that
Project and the evidence needed to judge whether it was reached.

Research investigates a bounded question for the Project and Goal using source
evidence. Experiment produces new observations using a declared protocol and
conditions. Research aggregates evidence; Experiment records the empirical
test; separate findings or owner decisions state conclusions.

This connection has two directions:

```text
product thesis -> explains why a Project and Goal matter
Research       -> informs the Goal using existing sources and observations
Experiment     -> tests one bounded realization and produces run evidence
findings       -> synthesize evidence without promoting themselves
```

One Project or Goal cannot prove the whole thesis. It can provide evidence for
or against a specific realization while keeping scope and counterevidence
visible. The canonical meanings and document contracts live in
[Goal and Project](../goals/README.md), [Research](../research/README.md), and
[Experiment](../experiments/README.md).

## Governance And Authority

In product language, **authority** is the bounded right to make a particular
consequence real. It answers:

```text
who or what + action + target + scope + conditions + lifecycle point
    = one bounded authority envelope
```

**Governance** is how CyberAlchemy keeps authority, ownership, evidence,
conditions, and consequence boundaries visible and intact while work moves.
The system should carry routine governance burden: find the narrowest
responsible route, preserve evidence, check the allowed envelope, and show what
an action cannot do. Human-visible ceremony should be proportionate and
concentrated where the consequence changes.

Governance is always present as a product invariant, but it does not require a
human-interrupting gate for every harmless operation. Reading, exploration,
drafting, preview, and reversible local work should stay lightweight. An
explicit authority boundary becomes visible when work moves, for example, from:

```text
candidate       -> canonical
recommendation  -> owner decision
preview         -> execution
local           -> shared, public, deployed, or external
accepted scope  -> an effect or a successor action
```

These distinctions must not collapse:

```text
ownership          != authority
participation      != authority
evidence           != authority
recommendation     != decision
candidate          != canonical
preview            != execution
handoff            != acceptance
validation PASS    != promotion
accepted envelope  != publication or successor authority
```

Ownership means responsibility for work or a decision route. Evidence supports
a claim or choice. Neither one automatically grants authority. A product record,
ontology node, recommendation, generated artifact, or successful test also
cannot grant itself authority.

The stable CyberAlchemy v2 authority model owns the detailed authority kinds,
postures, and owner routes. This product thesis states why those distinctions
matter to the person using CyberAlchemy; it does not redefine them or approve
an authority envelope.

## Product Ergonomics

Ergonomics here is not visual polish or simple ease of use. We believe the
product is ergonomic only when the work fits the person, task, and moment while
preserving important domain consequences and human control.

The system carries avoidable memory, routing, reconstruction, and coordination
burden. It recognizes or accepts meaningful work moments, presents the smallest
useful owner-safe choice, adjusts timing, task shape, and detail through explicit
context, and preserves flow, evidence, non-action, and continuity. The person
keeps judgment over consequential choices.

An ergonomic CyberAlchemy work surface should make it possible to answer:

- where should I start;
- what kind of work moment is this and where does it sit in the larger work arc;
- what objective, task state, and domain priority am I looking at;
- what is decided, current, historical, stale, or unresolved;
- which evidence and relationships matter;
- which small set of actions is relevant now, what each would do, and what each
  must not do;
- which action fits the available attention, time, and collaboration context
  without hiding important work;
- who owns the next action and what evidence or receipt it owes; and
- how can I park, reject, resume, or hand off without reconstructing the whole
  conversation.

Human context must be explicit, opt-in, local, reviewable, and allowed to remain
unknown. The product must not infer fatigue, focus, confidence, or other private
state as surveillance data. It must not hide domain-critical work merely because
that work is demanding.

## Progressive Context Resolution And Sufficiency

Define should not force a person to repeat work context that is already visible,
but it must not silently turn machine inference into a user statement. For each
bounded goal it resolves context in this order:

1. intent context and related references supplied by the person;
2. relevant work context visible in the current context window;
3. relevant work context preserved in the current Define Session; and
4. an explicit invitation to provide more context when the available material is
   insufficient or the decision remains indeterminate.

The second and third sources produce candidate context only. Every candidate must
retain its source, selector or session revision, derivation posture, and confidence
so the person can inspect, correct, reject, or replace it. Define evaluates the
bounded material against the needs of the stated job and records one of three
results: `sufficient`, `insufficient`, or `indeterminate`. Only `sufficient` lets
the capability continue as though the context requirement is met. The other
results preserve the gap and ask whether the person wants to provide more context;
silence is not consent and inferred context creates no authority.

The private semantic-judgment evaluator witness is evidence that a frozen,
provenance-bearing request can be reduced deterministically and can return an
insufficient outcome. It is not yet a Define context evaluator, a complete
reasoning engine, an authority resolver, or evidence that this product behavior
has been implemented.

Necessary detail may remain dense, but it needs a clear entry point and a short
path to a useful action. CyberAlchemy removes avoidable friction while retaining
the friction required for judgment, consent, privacy, evidence, and ownership.

## Who Participates

| Actor | Product responsibility |
| --- | --- |
| Human Participant | Supplies intent and judgment, answers or challenges important questions, and keeps control of consequential choices. |
| Machine Collaborator | Finds prior evidence, proposes structure, checks consistency, prepares work, and acts only inside its allowed boundary. |
| Work Owner | Owns a definition, lifecycle, decision, receiving stage, or next action. Ownership must be explicit; it is never inferred from a generated artifact. |

One person can hold more than one role. The roles remain separate because
participation, ownership, judgment, and authority are not the same thing.

## How CyberAlchemy Creates Value

In product language:

```text
human intent and explicit context
    + connected meaning, work state, evidence, domain priority, and ownership
    -> a meaningful work moment is noticed or selected
    -> a small explainable choice with its bounded authority visible
    -> an action shaped to the person, task, and moment
    -> a reviewable next step
    -> work that can continue across sessions, people, and machines
```

In system language:

```text
sense -> decide -> route -> act -> test -> preserve -> hand off -> re-sense
```

In DomainSpec language, this product meaning can later be projected as typed
actors, capabilities, rules, outcomes, operations, events, interfaces, and
relationships. That projection must preserve the business meaning; it must not
replace it.

## Why Define Exists

Define is the first concrete CyberAlchemy capability modeled by this thesis.
Before Design chooses a solution, Define makes the required concepts visible
and records one honest state for each:

- reuse an existing meaning;
- specialize an existing meaning for this work;
- propose a new candidate meaning; or
- keep the concept as a visible open question.

Define matters because a design built on missing or conflicting meaning can
look precise while solving the wrong problem. Its useful result is a Definition
Pack that Design can inspect, challenge, and accept as input.

Before treating context as adequate, Define applies the progressive context
resolution and sufficiency rule above. This reduces avoidable repetition while
keeping inference visible and preserving an honest request for more context when
the available work evidence cannot support the job.

Define does not make a term canonical, approve Design, authorize
implementation, or prove that all human intent was captured.

## Language-Guided Agent Work

An agent cannot apply a shared language from a general instruction such as
"use the ubiquitous language." At the start or resumption of Define, the agent
needs one **Language Context View** bounded to the language, context, intended
use, and exact source digests relevant to that work.

The view makes the usable language explicit: preferred expressions, concept
identities, business, domain, and product meanings, current dispositions,
owners and evidence, candidate system realizations, relationship vocabulary,
known conflicts, and blocked uses. Define reuses those exact bindings when they
fit. When a binding is missing, stale, ambiguous, conflicting, or still owned
by an unresolved decision, Define specializes, proposes, or keeps the matter as
a visible question. It must not silently invent equivalence, choose an open
DomainSpec realization, or treat a familiar label as owned meaning.

The Definition Pack preserves the identity and digest of the Language Context
View and the bindings it applied. A relevant source change makes that view
stale and requires a new resolution before it can support continued work.

Language consultation gives the agent bounded context. It does not transfer
meaning ownership, accept a definition, select an unresolved realization,
grant authority, or prove that the agent used the language correctly.

## Product And Delivery Form

The **CyberAlchemy Product** is the candidate governed human-machine work
system described here.

The **CyberAlchemy v2 Repository** is the project-local stable repository
candidate defined by `CAV2-D9`. It is intended to carry authority, ontology,
inventory, definitions, rules, evidence routes, and implementation surfaces.

The current premise is that the repository is an important delivery form for
the product. It is still open whether it is the whole product, one product in a
suite, or the base below several products.

## Product Hypotheses To Validate

These hypotheses test whether a realization delivers the principles. They do
not define whether the principles are first-order product commitments:

- people doing complex system work lose time and confidence when context,
  evidence, decisions, and ownership are disconnected;
- a visible shared work model can reduce that burden;
- recognizing meaningful work moments and offering small explainable choices
  can reduce coordination, switching, and context-recovery burden;
- fitting task shape and timing to explicit human context can improve flow
  without hiding domain priority;
- people will accept machine help when important choices and boundaries remain
  legible;
- people can move faster when the product carries routine governance work and
  makes authority explicit only at real consequence boundaries;
- preserved open questions are more useful than silent guesses;
- better continuity improves the next stage, not only the document produced by
  the current stage.

## Evidence That Would Require Revision

Evidence can show that a realization violates the principles or that the product
approach does not create the intended outcomes. The realization—and, if the
failure is systemic, the thesis—must be revised when:

- users do not understand the next step more clearly;
- users cannot quickly find the current objective, evidence, open questions,
  owner, or next action;
- the system repeatedly suggests the wrong action for the moment, overwhelms the
  person with choices, or turns assistance into interruption;
- task-fit behavior favors comfortable work over domain-critical work;
- a person cannot tell who or what may make the next consequence real, or the
  scope and conditions of that authority;
- governance becomes repeated ceremony for harmless work, or becomes so hidden
  that consequential work crosses a boundary without a visible owner route;
- recovering or maintaining the governed context costs more than it saves;
- work still loses important meaning, evidence, or ownership at handoff;
- apparent improvement depends on hiding choices or weakening privacy;
- human context is inferred, retained, or scored without an explicit local and
  reviewable contract;
- the Definition Pack does not help Design or reduces its ability to challenge
  assumptions;
- users prefer a materially simpler approach for the same class of work.

## Ontology References

- Product: `CA2-PRODUCT-CYBERALCHEMY`
- Thesis: `CA2-THESIS-GOVERNED-HMI`
- Problem: `CA2-PROBLEM-DISCONNECTED-WORK`
- Work loop: `CA2-CAP-GOVERNED-WORK-LOOP`
- Define: `CA2-CAP-DEFINE-SHARED-MEANING`
- Language context resolution: `CA2-CAP-RESOLVE-LANGUAGE-CONTEXT`
- Language context product output: `CA2-OUTPUT-LANGUAGE-CONTEXT-VIEW`
- Define language-application rule:
  `CA2-RULE-DEFINE-LANGUAGE-APPLICATION`
- Progressive context sufficiency rule:
  `CA2-RULE-DEFINE-CONTEXT-SUFFICIENCY`
- Product output: `CA2-OUTPUT-DEFINITION-PACK`
- Desired outcomes: `CA2-OUT-REVIEWABLE-NEXT-STEP` and
  `CA2-OUT-WORK-CONTINUITY`
- Product ergonomics rule: `CA2-RULE-WORK-ERGONOMICS`
- Bounded authority rule: `CA2-RULE-AUTHORITY-BOUNDED-VISIBLE`
- Useful governance rule: `CA2-RULE-GOVERNANCE-SERVES-WORK`

These are candidate ontology identifiers with `authority_effect: none`. They do
not create canonical vocabulary by being referenced here.
