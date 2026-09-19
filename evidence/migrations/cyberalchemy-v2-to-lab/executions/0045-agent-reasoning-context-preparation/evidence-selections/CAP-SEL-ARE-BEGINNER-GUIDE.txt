---
title: Agent Reasoning Engine Guide for the cyberalchemy-orchestrator Author
status: draft-for-teammate-review
audience: cyberalchemy-orchestrator author, new to the Agent Reasoning Engine
source_state_as_of: 2026-08-13
schema: BEGINNER-GUIDE-SCHEMA.yml
authority_effect: none
---

# Agent Reasoning Engine: the bridge from orchestration to judgment

You already built `cyberalchemy-orchestrator`, which can refuse an agent launch
when its required binding or lifecycle evidence is missing. The Agent Reasoning
Engine explores a different decision: given fixed facts and rules, what
conclusion follows? Two small reasoning packages work locally today, but they
are not currently integrated with the orchestrator or with each other as a
complete engine. Advice is not permission.

## 1. Where does reasoning begin after orchestration ends?

The orchestrator answers whether a particular piece of agent work may launch
and how its lifecycle is recorded. The reasoning engine asks what follows from
the information supplied for a domain decision. A well-authorized dispatch can
still reach a weak, contradicted, or incomplete conclusion.

Keep four results separate:

| Result | Question it answers | What it cannot do |
|---|---|---|
| Launch authorization | May this agent work start? | Prove its domain conclusion |
| Route advice | Which fixed route appears to fit? | Select or launch an agent |
| Semantic recommendation | What follows from these facts and rules? | Permit a real action |
| Effect permission | May this one exact action happen? | Grant wider authority |

The shared pattern is deliberate boundaries and fail-closed behavior. The
responsibilities differ: orchestration owns launch and lifecycle; this project
owns route comparison and semantic judgment. Never infer
`RecommendedUnderSnapshot` from `status=launch-authorized`, or the reverse.

Start from a concrete research question:

> Can the Agent Reasoning Engine use ACI-owned journal facts without becoming
> a second lifecycle writer?

That question crosses source ownership, lifecycle recording, reasoning input,
and evidence. If it needs several source sets, independent viewpoints, or work
in parallel, [`domainspec-subagents-strategy`](../../../implementation/domainspec/internal_tools/subagents-dispatch-hooks/skills/domainspec-subagents-strategy/SKILL.md)
treats it as a research-dispatch candidate. The strategy governs how the
research is admitted and run. It does not decide whether the eventual finding
is true.

```mermaid
flowchart TB
    accTitle: Governed research dispatch and separate semantic judgment
    accDescr: A research question enters a confirmed DomainSpec dispatch lifecycle. Closed findings remain evidence. A separate and currently unwired reasoning path asks what follows from fixed evidence and rules.

    subgraph dispatch["Governed research dispatch — DomainSpec adapter"]
        question["Research question"] --> trigger["Dispatch trigger check<br/>+ read-only Inventory map"]
        trigger --> sheet["Validated dispatch sheet<br/>+ two independent challenge passes"]
        sheet --> confirmation{"Explicit human confirmation?"}
        confirmation -->|no| stop["STOP<br/>Do not register or start agents"]
        confirmation -->|yes| register["Register dispatch"]
        register --> explorers["Run and join explorers"]
        explorers --> researchLog["Append verbatim explorer returns<br/>to research.md"]
        researchLog --> review["Synthesize → independent reviews"]
        review --> closure["Close cited evidence"]
        closure --> findings["Writer authors findings.md<br/>EVIDENCE, NOT AUTHORITY"]
        findings --> audit["Auditor → acceptance checks<br/>→ index → closeout"]
    end

    subgraph semantic["Separate semantic path — no current runtime edge"]
        snapshot["Owner-admitted evidence + fixed rules<br/>for one reasoning snapshot"] --> reasoning["Agent Reasoning Engine<br/>CANDIDATE WHOLE"]
        reasoning --> advice["Semantic recommendation<br/>NOT EFFECT PERMISSION"]
    end
```

`domainspec-subagents-strategy` is a DomainSpec dispatch adapter, not the
orchestrator and not part of the reasoning engine. A successful research
lifecycle proves that the research process completed under its contract; it
does not prove its findings true. `research.md` preserves the explorers'
verbatim returns; `findings.md` is written only after cited evidence closes.
Both remain research evidence.

There is no implemented edge from `findings.md` to a reasoning snapshot. A
future owner would have to select and admit evidence before semantic
evaluation. Even then, the evaluator would return advice, not implementation
selection or effect permission.

## 2. What works today?

There is no general reasoning service to start. There are two independent Node
libraries inside a larger proposed design.

```mermaid
flowchart LR
    accTitle: Two disconnected implemented packages
    accDescr: The resolver returns route advice. Separately, the evaluator returns a semantic outcome. There is no edge between the packages.

    subgraph routing["Implemented local library 1"]
        direction TB
        routeInput["Prepared typed request<br/>+ fixed route list"] --> resolver["Intent route resolver"]
        resolver --> routeAdvice["Route disposition<br/>ADVISORY ONLY"]
    end

    subgraph judgment["Implemented local library 2"]
        direction TB
        judgmentInput["Fixed facts + rules<br/>for one judgment"] --> evaluator["Semantic judgment evaluator"]
        evaluator --> semanticOutcome["Typed semantic outcome<br/>NOT EFFECT PERMISSION"]
    end
```

| Surface | Current truth |
|---|---|
| Semantic judgment evaluator | Implemented locally; its 16 tests pass |
| Intent route resolver | Implemented locally; its 34 tests pass |
| Complete Agent Reasoning Engine | Designed, not implemented as a complete runtime |
| Orchestrator connection and real effects | Future and blocked; no current integration |

The evaluator and resolver are siblings. Neither imports or calls the other.
Passing tests show that the checked bytes behave as tested; they do not prove
product integration, release readiness, or permission to begin new work.

## 3. What semantic decision is still missing in a correct dispatch?

Use a refund review as the smallest example. The orchestrator might correctly
authorize and record a review run. That does not decide whether the customer is
eligible for a refund. The evaluator still needs the policy rules and relevant
observations fixed for that one review.

The project calls those fixed inputs a **reasoning snapshot**. It is similar to
the exact inputs and digests your ACI bridge binds before launch: it makes one
decision traceable. It differs in owner and job. A reasoning snapshot is not an
ACI event, ledger row, or projection, and it does not authorize a launch.

For the refund example, changing one fact changes the named result:

- required support is present: `RecommendedUnderSnapshot`;
- important support is missing: `Deferred.Insufficient`;
- a grounded fraud hold defeats eligibility: `Ineligible.Defeated`;
- unrelated agent agreement changes nothing;
- a recommendation plus a failed effect check produces zero effect attempts.

The example stops at an in-memory test marker. It cannot send a real refund.

## 4. How does the semantic evaluator work?

In plain language, the evaluator follows this order:

1. Check whether this review may start, and save that decision.
2. If it passes, compare the fixed facts with the fixed rules.
3. Save the answer and the reasons used to reach it.
4. Stop unless the answer is a recommendation.
5. For a recommendation, check permission for one identical test action.
6. Only that exact pass may reach the in-memory test double.

```mermaid
flowchart TB
    accTitle: Semantic evaluator gate sequence
    accDescr: Entry may stop evaluation. Only RecommendedUnderSnapshot reaches the separate exact-effect gate, whose pass reaches an in-memory test double.

    entry["Save entry decision"] --> entryVerdict{"Entry verdict"}
    entryVerdict -->|non-pass| entryStop["Stop or pause<br/>zero evaluation and effects"]
    entryVerdict -->|pass| evaluate["Compare fixed facts<br/>with fixed rules"]
    evaluate --> receipt["Save the outcome,<br/>reasons, and residue"]
    receipt --> outcome{"Semantic outcome"}
    outcome -->|all other outcomes| semanticStop["Close with zero effects"]
    outcome -->|RecommendedUnderSnapshot only| effectGate["Check permission for<br/>one identical test action"]
    effectGate -->|non-pass| effectStop["Keep the recommendation<br/>zero effect attempts"]
    effectGate -->|pass| testDouble["One idempotent test attempt<br/>IN-MEMORY TEST DOUBLE ONLY"]
```

The function that coordinates this order is
[`executeWitness`](../../implementation/agent-reasoning-engine/packages/semantic-judgment-evaluator/src/execute.mjs).
Its entry gate is similar to an orchestrator gate because both can stop work.
It differs because it controls entry to a semantic evaluation, not an agent
launch. Its reasoning receipt records a derivation; it is not an ACI lifecycle
receipt.

The evaluator returns exactly one of these outcomes:

| Input or authority problem | Domain result | Later invalidation |
|---|---|---|
| `InvalidInput` | `Ineligible.Defeated` | `Invalidated` |
| `UnauthorizedCatalog` | `Deferred.Insufficient` | |
| `OutOfDomain` | `EscalateOwner` | |
| | `RecommendedUnderSnapshot` | |

Start with the
[`refund-eligibility.json`](../../implementation/agent-reasoning-engine/fixtures/evaluator-v1/refund-eligibility.json)
fixture, then follow
[`src/reducer.mjs`](../../implementation/agent-reasoning-engine/packages/semantic-judgment-evaluator/src/reducer.mjs)
for the checks and
[`src/receipt.mjs`](../../implementation/agent-reasoning-engine/packages/semantic-judgment-evaluator/src/receipt.mjs)
for the saved explanation.

## 5. How does the route resolver differ?

The resolver compares a prepared request with an owner-supplied route list. It
checks both shapes, removes routes that violate exclusions or requirements, and
uses only explicit preference edges from that list. If an important detail is
missing or several routes still fit, it preserves the ambiguity.

```mermaid
flowchart TB
    accTitle: Intent route resolver decision flow
    accDescr: The resolver validates fixed inputs, applies owner-supplied preferences, and returns one of four advisory dispositions without dispatch or execution.

    inputs["Prepared request<br/>+ fixed route list"] --> valid{"Both contracts valid?"}
    valid -->|no| invalid["invalid"]
    valid -->|yes| eligibility["Evaluate exclusions<br/>and requirements"]
    eligibility --> preference["Apply only explicit<br/>owner-supplied preference edges"]
    preference --> classify{"Classify what remains"}
    classify -->|one fitting route| candidate["candidate<br/>ADVISORY ONLY"]
    classify -->|missing detail or overlap| ambiguous["ambiguous<br/>+ one question"]
    classify -->|complete request, no route| noMatch["no-match"]
```

[`resolveIntentRoute`](../../implementation/agent-reasoning-engine/packages/intent-route-resolver/src/resolve.mjs)
returns one of four results:

- `candidate`: one fitting route remains and is not outranked;
- `ambiguous`: information is unresolved or routes overlap, with one question;
- `no-match`: the request is complete, but no route fits;
- `invalid`: the request or route list breaks its contract.

This may feel like a deterministic pre-filter in the orchestrator. The shared
pattern is comparison against a fixed contract. The difference is that this
package owns neither the orchestrator catalog nor dispatch authority. It does
not understand free-form language, discover capabilities, approve work, launch
an agent, or execute an effect. Every disposition carries
`authority_effect: none`.

Trace the fixed cases in
[`cases.json`](../../implementation/agent-reasoning-engine/packages/intent-route-resolver/test/fixtures/witness/cases.json),
then read [`src/request.mjs`](../../implementation/agent-reasoning-engine/packages/intent-route-resolver/src/request.mjs),
[`src/catalog.mjs`](../../implementation/agent-reasoning-engine/packages/intent-route-resolver/src/catalog.mjs),
and [`src/eligibility.mjs`](../../implementation/agent-reasoning-engine/packages/intent-route-resolver/src/eligibility.mjs).

## 6. How could this relate to ACI without taking over ACI?

Your orchestrator already owns its Session, journal, capability, and dispatch
lifecycle contracts. The accepted reasoning-engine direction is
**ACI-subordinate**: a future connection should consume ACI-owned lifecycle
facts rather than introduce another writer for them. Semantic derivation and
the reasoning receipt remain reasoning-engine responsibilities.

That is a design boundary, not compatibility evidence. Today:

- the resolver output is not wired into evaluator input;
- neither package is wired into `cyberalchemy-orchestrator`;
- most surrounding engine components remain proposed or blocked;
- no real effect adapter exists.

```mermaid
flowchart LR
    accTitle: Proposed ACI subordinate seam
    accDescr: Orchestrator ACI owns lifecycle facts. A dashed future seam may supply them to semantic derivation, but no integration exists. The resolver remains separate.

    subgraph existing["cyberalchemy-orchestrator ACI — EXISTING OWNER"]
        aci["Session + journal + capability<br/>+ dispatch lifecycle facts"]
    end

    subgraph reasoning["Agent Reasoning Engine — NOT INTEGRATED"]
        semantic["Semantic derivation<br/>+ reasoning-receipt content"]
        resolverBoundary["Intent route resolver<br/>STANDALONE; NO EVALUATOR EDGE"]
    end

    aci -.->|FUTURE SEAM<br/>ABSENT TODAY| semantic
```

The dashed edge is a design direction, not a runtime call. Shared vocabulary
does not establish matching schemas, owners, compatibility, or permission.

## 7. Which files answer which question?

The private CAV2 project separates plans from executable bytes:

```text
cyberAlchemy-v2/
├── development/agent-reasoning-engine/     # meaning, design, plans, gates
└── implementation/agent-reasoning-engine/  # the two working libraries
```

| Question | Start here |
|---|---|
| What is the proposed whole? | [`spec/SPEC.md`](spec/SPEC.md) |
| Where are responsibilities separated? | [`design/ARCHITECTURE.md`](design/ARCHITECTURE.md) |
| What may happen next? | [`.craft/ledger.yml`](.craft/ledger.yml) and [`planning/WORK-PACK.md`](planning/WORK-PACK.md) together |
| What actually runs? | Source and tests under [`implementation/agent-reasoning-engine`](../../implementation/agent-reasoning-engine/) |
| What is the familiar comparison? | [`projects/cyberalchemy-orchestrator/README.md`](../../../projects/cyberalchemy-orchestrator/README.md) |
| How is multi-agent research governed? | [`domainspec-subagents-strategy/SKILL.md`](../../../implementation/domainspec/internal_tools/subagents-dispatch-hooks/skills/domainspec-subagents-strategy/SKILL.md) |

The orchestrator is a comparison source and future dependency, not authority
for reasoning-engine semantics. Historical receipts prove only their exact
runs; they are not a substitute for current code and tests.

## 8. What should I do in my first 90 minutes?

From the repository root, run the two complete suites:

```bash
cd /home/vrondelli/projects/domainspec-core
node --version

node --test \
  cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/semantic-judgment-evaluator/test/*.test.mjs

node --test \
  cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/intent-route-resolver/test/*.test.mjs
```

Node 22 is sufficient, and neither package needs third-party runtime packages
for these tests. They are libraries, not services, so there is no `start`
command.

Then trace one refund case and one resolver case. For each, say aloud: input,
check, named result, and stopping point. Finish by comparing launch
authorization, semantic recommendation, and exact-effect permission. That gives
you the local difference without another introduction to orchestration.

On 2026-08-13, these commands passed 16 evaluator tests and 34 resolver tests
under Node `v22.13.0`.

## 9. When is it safe to edit code?

Reading, running tests, and tracing fixtures are available now. Editing needs
one selected task, an agreed file boundary, and named review checks.

The current documents disagree about the next move. The lifecycle ledger and
its human view still say to author the ACI-subordinate plan revision. The newer
work pack says that revision is already authored, but also says
`selected_swu: none` and `implementation_authorized: false`. It adds a
closeout-sync blocker absent from the ledger.

Do not resolve that disagreement by picking the newest sentence. Green tests
do not select an SWU. Ask the lifecycle owner to synchronize the sources and
name the exact task before mutation. Also, do not hand-edit generated run
receipts; a changed implementation needs newly owned evidence, not altered
history.

## 10. Am I ready to join a scoped task?

You are ready for a task conversation when you can answer these in your own
words:

1. What decision remains after a dispatch is correctly authorized?
2. How do route advice, semantic recommendation, and effect permission differ?
3. What does each local package return, and where does it stop?
4. Which ACI patterns are useful comparisons, and where does each comparison
   stop?
5. Why does existing orchestrator ACI not prove current reasoning-engine
   integration?

Then retell both code paths from one fixture and state what is still absent. The
safe next action is to run and trace the tests, surface any stale source or
confusing boundary, and wait for one synchronized task before editing. That is
enough to join the project without pretending the complete engine already
exists.
