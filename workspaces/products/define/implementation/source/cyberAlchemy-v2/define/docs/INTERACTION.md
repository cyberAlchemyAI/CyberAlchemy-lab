# Define Interaction And Session Model

Status: perennial candidate. No authority effect.
Owner: CyberAlchemy v2 Define runtime owner.

In plain terms: this is a long-lived proposal. It grants no permission to act.

## Purpose

A **Define Session** is the saved record for one goal. It keeps the goal, intent,
context, current question, earlier questions and answers, sources, evidence,
handling choices for concepts, owners, open gaps, and permission limits
together.

The interactive CLI and chat are two ways to read and update that same saved
session. A person can stop in one interface and continue in the other without
reconstructing the work from memory.

This is the target interaction model. The full software that would save and
coordinate this session does not exist yet.

The target is not a blank design. It reuses the Arcanum Define interaction and
stage mechanics and the DomainSpec v2 CLI system model. Those sources support
the session fields, question flow, and shared CLI/chat direction. They do not
yet show that the complete CyberAlchemy runtime works or that people find it
easy to use.

## Interaction Principles

1. Show one useful question at a time.
2. Show why the question matters to the current goal.
3. Keep the goal, intent, context, context provenance, and current sufficiency
   status visible.
4. Preserve earlier questions, answers, corrections, sources, and open gaps.
5. Let the person answer, defer, refuse, correct the context, or route the
   question to an owner.
6. Never save silence or observed behavior as an answer.
7. Keep source searches and link checks quiet.
8. Ask the person before changing accepted meaning, choosing an owner, granting
   permission, or changing a system outside this saved session.
9. Show what is complete, what is open, and what blocks the stated use.
10. Prefer explicit context, then current-window context, then saved-session
    context, and ask for more only when the bounded evidence remains
    insufficient or indeterminate.

These rules make ease of use concrete: fewer repeated explanations, one visible
question, resumable work, and no hidden gap.

## Define Session

One session records:

- session ID;
- goal, intent, and context;
- context candidates with source kind, source reference or session revision,
  derivation posture, confidence, and user disposition;
- the latest context sufficiency evaluation, named missing context, and
  evaluator receipt reference;
- goal owner and the person, team, or tool that will use the pack;
- current question;
- question and answer history;
- exact sources and evidence;
- current concept handling choices, called dispositions;
- open gaps and conflicts;
- decision owners;
- check results;
- current work state; and
- allowed uses and blocked actions.

The session is more than a chat transcript. It is the saved state of the Define
work.

## Context Resolution Contract

The runtime evaluates context at session creation and whenever intent, context,
references, the current context window, the relevant session revision, or the
requirements of the current Define job change.

The resolution policy processes these sources without skipping ahead:

1. `explicit-user` — intent context and related references supplied by the user;
2. `current-window-inference` — relevant work context visible in the current
   context window;
3. `saved-session-inference` — relevant work context from the current Define
   Session; and
4. `additional-context-request` — a visible invitation when evaluation remains
   `insufficient` or `indeterminate`.

Each inference is stored separately from explicit context and carries exact
provenance. A later source may fill a gap but may not overwrite, reinterpret, or
out-rank explicit user context. Conflicts become visible residue.

The sufficiency evaluator receives a frozen requirement set and frozen candidate
digests. It returns `sufficient`, `insufficient`, or `indeterminate`, together
with derivation and residue. The result authorizes nothing. A sufficient result
allows the Define workflow to continue only within its existing authority
ceiling. The other results open one focused request asking whether the user wants
to provide more context; refusal, deferral, and correction are recordable
answers, while silence is not an answer.

## Question Contract

A **contract** is the fixed set of fields each question must carry. A Define
question records:

- question ID and session ID;
- the missing concept, context, or decision;
- why it matters now;
- related concepts, sources, and evidence;
- who may answer or decide;
- whether the gap blocks the stated use;
- answer state; and
- challenge or routing instructions.

A question remains visible until it is answered, deferred, routed, or closed
with a recorded reason.

## Answer Contract

An answer records:

- question ID;
- responding person or owner;
- the response, deferral, refusal, or correction;
- time and evidence context;
- where the answer applies;
- whether the responder may decide this exact matter; and
- any new question created by the answer.

Recording an answer does not make it official or approved. **Authority** means
permission to make one exact decision count. The answer's effect depends on the
responder's existing authority and the stated context.

## CLI Wizard

The CLI asks one question at a time while keeping a stable session summary
visible. It should show:

- goal, intent, and context;
- context sources and the current sufficiency status;
- current question and why it matters;
- available choices plus free-form input;
- related sources and decision owner on request;
- progress through required concepts;
- open and blocking questions; and
- commands to pause, resume, inspect, or export the pack.

The exact terminal layout and command names remain design choices.

## Chat View

Chat shows the same saved session in conversational form.

When chat or the CLI changes a question or answer, the runtime must check:

1. the session ID is the same;
2. the question ID is the same; and
3. the responder may make that exact decision.

Both interfaces update one saved session record. Neither keeps a separate copy
that can silently disagree.

## Persistence And Transport Boundary

**Persistence** means saving the session so it can be resumed.

**Transport** means how the CLI and chat exchange session data.

An **IPC socket** is one possible data channel between local processes.

This document requires resumable shared state. It does not choose an IPC socket,
database, file format, container layout, data retention rule, synchronization
protocol, or security model.

Runtime design must compare those choices against privacy, recovery, use by two
interfaces or people at the same time, portability, and operating cost. A
container may help test the runtime. It is not part of the product meaning of
Define.

## Example

Example only: this does not define “customer,” appoint a real billing-domain
owner, or authorize implementation.

The CLI may show:

    Goal: A customer can request a refund
    Context: Online-shop refund eligibility
    Current question: Which owned definition of “customer” applies here?
    Why it matters: Eligibility rules depend on this answer
    Suggested decision owner: Billing-domain owner
    Status: Open — blocks eligibility-rule implementation
    Actions: answer | defer | correct context | route to owner

The displayed actions are available only inside the person's recorded scope.

The person may defer the question in chat. When the CLI resumes, it shows the
same question as deferred. Silence is never saved as an answer.

## Failure And Recovery

If an interface disconnects or saving fails:

- keep the last confirmed session state;
- show which change was not saved;
- do not invent an answer;
- do not discard an open question; and
- do not show an unconfirmed change as complete.

The exact recovery rules still need to be written and tested.

## Claim Ceiling

This document states an evidence-backed target interaction model. It does not
establish a finished wizard, saved runtime state, CLI and chat synchronization,
security, accessibility, or measured reduction in user effort.
