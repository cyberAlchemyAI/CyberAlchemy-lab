# Definition Pack Contract

Status: perennial candidate. No authority effect.
Owner: CyberAlchemy v2 Definitions Governance owner.

In plain terms: this is a long-lived proposal. It grants no permission to act.

## Purpose

The **goal** is the specific result wanted. The **intent** is the original reason
for that goal.

An important term or idea needed for the work is called a **concept**. The place
where it applies—such as one feature, domain, or user group—is its **context**.

A **source** is the exact place information came from. **Evidence** supports a
statement or decision. A **relationship** is a named link between concepts. An
**owner** is the person or role allowed to decide one exact matter.

Define produces one checked bundle for a stated use. The bundle keeps the goal,
intent, context, required concepts, sources, evidence, owners, relationships,
and open questions together. It is called a **Definition Pack**.

The person, team, or tool that uses the pack is called its **consumer**.

Each required concept has one current handling choice. That choice is called its
**disposition**.

A Definition Pack may reference records from the Define
[handled-definitions registry](../handled-definitions.json). The Pack freezes the
exact records used for one consumer and intended use; it does not turn the
registry into canon or make a registry record suitable for a different context.

Here, **canonical** means formally accepted by the configured definition owner.

This document lists what a Definition Pack must contain and what its checks do
and do not prove.

## Required Content

A pack contains:

- pack ID and the ID of the saved Define Session;
- the goal and its limits;
- the original intent;
- the context where the pack applies;
- context candidates and their explicit, current-window, or saved-session
  provenance;
- the latest context sufficiency status, frozen requirement and candidate
  digests, derivation, residue, and evaluator receipt reference;
- goal owner and named consumer;
- the list of required concepts;
- one current disposition for every concept;
- reused, specialized, or proposed definition text;
- the context and limits of each definition;
- exact sources and evidence;
- named relationships between concepts;
- decision owners;
- open questions and conflicts;
- check results and the time when the sources were last confirmed;
- allowed uses;
- blocked actions; and
- a challenge or refresh route.

## Concept Dispositions

| Disposition | When to use it | What the pack records |
| --- | --- | --- |
| reuse | An existing owned definition fits this context. | Exact source, source owner, version or file hash, context, and relationship to the goal. |
| specialize | An existing definition fits after its context is narrowed. | Parent definition, narrower context, decision owner, and a statement that the parent is not replaced. |
| propose | No current definition is sufficient, so a new candidate is offered. | Formal statement, plain explanation, project example, evidence, decision owner, candidate status, and authority effect none. |
| open | The meaning is missing, unclear, disputed, or waiting for an owner. | Question, reason, affected concepts, decision owner, whether the stated use must stop, and next action. |

Every required concept has exactly one current disposition. Older dispositions
stay in history, but two current dispositions for the same concept are a defect.

Derived context is not an answer. The Pack keeps inferred context separate from
user-supplied context and records whether the user accepted, corrected, rejected,
or did not review it. A `sufficient` evaluation means only that the bounded
context requirement for the named Define job was met under the recorded inputs.
It is not proof of complete intent, truth, approval, ownership, or authority.

## Acceptance Checks

A pack passes its structural checks only when:

1. the goal stays linked to its original intent;
2. the context, its provenance, the sufficiency result, and the required concept
   list are stated;
3. every concept has exactly one current disposition;
4. every source, evidence, owner, and relationship link works or is shown as an
   open gap;
5. every unresolved question is visible;
6. the consumer and intended use are stated; and
7. allowed uses and blocked actions are stated.

These checks show that the concepts needed for this use are recorded or clearly
open. When a concept reuses a canonical definition, its exact binding is
evidence of that definition's canonical status and source currency. Structural
checks alone do not establish that the reused definition fits this context,
that a new candidate is correct, or that either is complete for every future
use.

## Result Presentation

Every Define invocation that reaches a saved-candidate or later state must show
its resolved result to the caller in the same interaction. A path, receipt,
disposition table, or completion statement alone is insufficient.

The presented result must list every required concept and show:

- its current disposition and decision owner;
- for `reuse`, the selected canonical definition content and exact source
  identity, selector, and digest;
- for `specialize`, the specialized normative, formal, plain-language, and
  domain-context content together with its unchanged parent binding;
- for `propose`, the complete proposed normative, formal, plain-language, and
  domain-context content plus boundary and candidate posture;
- for `open`, the unresolved question, stop condition, and next owner action;
- applicable boundaries, open questions, allowed uses, blocked actions, and
  the result's claim ceiling.

Machine records remain canonical. The shown result is a deterministic human
projection and must be reproducible from those records and their exact pinned
sources. Presentation does not promote a definition, accept a pack, or grant
downstream authority.

## Consumer Use

The list below grants nothing new. The consumer may perform these actions only
inside its existing permission to make decisions and the pack's recorded
permission limits:

- accept the pack as input for one stated use;
- challenge a concept, context, definition, or source;
- continue while explicitly accepting named open questions, if it has authority
  to accept that risk;
- return questions to the same Define Session; or
- request a refreshed pack after the goal, intent, context, evidence, or scope
  changes.

Accepting a pack as input does not approve implementation.

## Version And Refresh

An important change creates a new pack state. Important changes include:

- goal, intent, or context;
- required concept list;
- current disposition;
- exact source version;
- owner;
- relationship;
- open question; or
- allowed use or blocked action.

The new state stays linked to the old state and records why it changed.

## Example

Example only: this does not define “customer,” appoint a real billing-domain
owner, or authorize implementation.

A small part of a refund Definition Pack could look like this:

    Concept: customer
    Context: online-shop refund eligibility
    Current disposition: open
    Question: Which owned definition of “customer” applies here?
    Consumer: refund product team
    Decision owner: billing-domain owner
    Blocked action: do not implement eligibility rules using an assumed meaning
    Evidence: links to the current billing and account definitions

This record makes the gap visible. It does not invent the answer.

## Boundaries

A Definition Pack is not:

- the canonical definition store;
- the complete handled-definitions registry;
- a product, system, UX, UI, or brand solution;
- an implementation plan;
- proof that all human intent was captured;
- permission to execute downstream work; or
- measured proof of product outcomes.

Here, **canonical** means formally accepted by the owner through the configured
definition store. A candidate in a pack is not canonical.

## Claim Ceiling

This document is a candidate output contract. It does not make any file an
admitted canonical artifact, promote a definition, accept a runtime, or give the
consumer permission to act.
