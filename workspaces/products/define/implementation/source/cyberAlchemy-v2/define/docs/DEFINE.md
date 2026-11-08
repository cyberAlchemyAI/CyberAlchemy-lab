# Define Capability

Status: perennial candidate. No authority effect.
Owner: CyberAlchemy v2 product owner.

In plain terms: this is a long-lived proposal. It grants no permission to act.

## Purpose

Work depends on more than a task description. People also need to know:

- what result is wanted;
- why it matters;
- where the work applies;
- which terms and ideas must be understood;
- where current information came from;
- who may decide unclear points; and
- which questions are still open.

Define collects those answers before work starts and while it continues. When an
answer is missing, Define uses visible, provenance-bearing work context before
asking the person to repeat it. If that context is still insufficient or
indeterminate, Define records and asks the question instead of guessing.

## Goal And Intent

A **goal** is the specific result wanted, including its limits.

An **intent** is the original reason for that goal. It records the problem,
purpose, and desired change.

Example:

- Goal: a customer can request a refund.
- Intent: reduce manual support work without refunding the wrong person.

Define may clarify the wording, but it must keep the goal linked to the original
intent.

## Definition

A **concept** is an important term or idea that the work depends on. **Context**
says where that concept is being used, such as one feature, domain, user group,
or time period.

A **source** is the exact place information came from. **Evidence** is
information used to support a statement or decision. A **relationship** is a
named link between two concepts. An **owner** is the person or role allowed to
decide one exact matter.

CyberAlchemy Define is a capability with stated owners and permission limits. It:

1. keeps the goal and intent visible;
2. lists the concepts needed for this context;
3. finds existing definitions, sources, evidence, relationships, and owners;
4. asks a question when a concept is missing, unclear, or disputed;
5. records one current handling choice for every required concept; and
6. produces a checked bundle for the next person, team, or tool.

That handling choice is called a **disposition**:

- reuse;
- specialize;
- propose; or
- open.

The checked bundle is called a **Definition Pack**.

## Handled Definition Registry

Define keeps context-bound definition handling records in a separate candidate
registry. A record identifies the concept and context, states one current
disposition—reuse, specialize, propose, or open—and retains its exact sources,
decision owner, consumers, and challenge or refresh route.

The registry is not the canonical definition store. Its product owner owns the
registry asset, Definitions Governance stewards the record contract, source and
decision owners retain authority over meaning, and a later runtime may only
persist records under a separately accepted implementation contract. The
initial registry is empty because no real bounded Define context has yet
produced a handled record in this package.

## Why Define Exists

Teams lose time when:

- the same word has different meanings in different files;
- a correct definition is used outside its intended context;
- the reason for a choice is lost;
- nobody knows who may answer a question; or
- a question disappears between tools or sessions.

Define keeps each concept linked to its context, source, owner, and open
questions.

This capability definition already has evidence behind it. It reuses 10 active
CAV2 definitions, the CAV2 product thesis and product ontology, existing Arcanum
Define product contracts, standalone runtime evidence, and the current system ontology. The current
validation receipt also shows that the package remains linked to the exact
recorded source bytes.

That evidence supports the problem, capability shape, method, authority limits,
and feasibility. We still need measured use evidence to know how much the
finished product reduces repeated explanations, hidden disagreements, or user
effort.

## Inputs

Define needs:

- a goal with stated limits;
- the intent behind the goal;
- the context where the result will be used;
- the person, team, or tool that needs the result;
- available documents, records, and other evidence;
- known owners; and
- existing questions or constraints.

Missing context follows the ordered resolution contract below. Any other missing
input becomes an open question.

## Context Resolution And Sufficiency

Define resolves the context needed for the stated job in a fixed order:

1. use intent context and related references explicitly supplied by the user;
2. if needed, derive candidate context from the current context window;
3. if still needed, derive candidate context from the current saved Define
   Session; and
4. if the bounded context is still insufficient or indeterminate, ask whether
   the user wants to provide more context.

Each derived item remains candidate context. Define records its source kind,
source reference or session revision, derivation posture, confidence, and any
conflict with explicit user context. Explicit user context always outranks a
machine-derived candidate, and the user may correct, reject, or replace any
candidate.

A semantic sufficiency evaluation is made against the needs of the current
Define job, not against an impossible standard of complete human intent. It
returns exactly one status:

- `sufficient` — the stated job can continue with the recorded bounded context;
- `insufficient` — named required context is missing; or
- `indeterminate` — the available evidence cannot support either conclusion.

Only `sufficient` satisfies the context prerequisite. The other states preserve
the missing or disputed context and create a visible invitation for more context.
Silence is not an answer. Inference, confidence, evaluator output, or a receipt
does not create user intent, ownership, approval, or authority.

The existing private semantic-judgment evaluator is a bounded feasibility
witness for deterministic reduction, provenance, residue, and insufficiency. It
is not yet the Define-specific evaluator described here and does not prove this
flow is implemented.

## Work

Define performs these steps:

1. resolve and evaluate the bounded context using the ordered source ladder;
2. list the concepts needed to understand the goal in that context;
3. search owned sources before creating a new definition;
4. check where each definition applies and who owns it;
5. record conflicting uses instead of silently choosing one;
6. ask one useful question when an important gap remains;
7. give every required concept one current disposition; and
8. check that sources, owners, relationships, context provenance, sufficiency,
   and open questions are visible.

## Result

The result is a [Definition Pack](DEFINITION-PACK.md). It keeps these items
together:

- goal, intent, and context;
- required concepts and dispositions;
- definitions and exact sources;
- evidence and relationships;
- owners;
- open questions;
- check results; and
- permission limits.

The next team may use the pack, challenge it, or send new questions back to
Define.

## Boundaries

Define clarifies concepts and context. It does not choose:

- product behavior;
- system architecture;
- UX flow or UI form;
- brand expression;
- implementation tasks;
- execution, publication, or deployment; or
- formally accepting a definition into the canonical definition store.

Define is not a mandatory stage before every design task. Use it when unclear
concepts or missing context would cause guessing, rework, or an ownership
conflict.

## Example

Example only: this does not define “customer” or authorize implementation.

A product team wants to add refunds.

    Goal: A customer can request a refund.
    Intent: Reduce manual support work without refunding the wrong person.
    Context: Refund eligibility for the online shop.

The concept “customer” is unclear. It could mean the buyer, account owner, or
gift recipient.

Define checks current sources and asks:

> Which owned definition applies to this refund context, and who may decide?

The current disposition may be reuse, specialize, propose, or open. Define
records the choice, source, owner, and remaining question. It does not design the
refund screen or choose the payment API.

## Owners

- The **goal owner** owns the goal and its original intent.
- A **source owner** owns meaning inside that source's stated context.
- The **CyberAlchemy v2 product owner** owns the candidate product meaning of
  Define.
- The **Definitions Governance owner** decides whether a definition candidate
  enters the canonical definition store.
- The **owner of the next use** decides whether the pack is suitable input for
  that use.

## Claim Ceiling

This candidate capability is supported by reused definitions, prior product and
ontology work, existing mechanics, runtime modeling, and source validation.
That evidence does not by itself establish measured customer outcomes, complete
understanding, a finished CyberAlchemy runtime, ease of use, canonical artifact
admission, definition promotion, or permission to execute downstream work.
