# Define Product

Status: perennial candidate. No authority effect.
Owner: CyberAlchemy v2 product owner.

A team wants to add refunds to an online shop. Everyone uses the word
“customer,” but they mean different people: the buyer, the account owner, or
the person who received the order. If the team starts designing before it
settles this, it may build the wrong refund rules.

Define helps the team find that confusion, examine what is already known, and
record what “customer” means for this job—or clearly say that the answer is
still open.

That is the product in one sentence:

> Before a team decides how to build something, Define helps it agree what the
> important words mean for this job and clearly marks what is still unknown.

## Purpose

Define keeps the meaning needed for one piece of work in one reviewable place.
It records:

- what the team is trying to do and why;
- where the work applies;
- which concepts matter;
- what existing sources say;
- what evidence supports each choice;
- who owns each decision; and
- which questions are still open.

The result is called a **Definition Pack**. Another person or tool should be
able to read it, challenge it, and continue the work without reconstructing the
whole conversation.

## Relationship To CyberAlchemy

Define is one module inside CyberAlchemy. It applies the wider
[CyberAlchemy Product Thesis](../../product/PRODUCT-THESIS.md) and
[product ontology](../../ontology/product/README.md) to one problem: making the
meaning needed for a task clear before the work moves on.

```text
CyberAlchemy keeps complex human-machine work connected.
    -> Define makes the important meaning clear for one task.
    -> Design or another named receiver reviews the Definition Pack.
    -> The wider work continues without losing intent, evidence, or ownership.
```

CyberAlchemy owns the wider product promise. Define owns this smaller part of
that promise. Define is not the whole CyberAlchemy product and cannot change
what CyberAlchemy means.

## Product Thesis

For every concept the next stage needs, Define records one of four honest
answers:

1. **Reuse** — an existing definition already fits.
2. **Specialize** — an existing definition fits after its scope is narrowed.
3. **Propose** — the work needs a new candidate definition.
4. **Keep open** — the team does not have a supported answer yet.

Each answer keeps its source, evidence, scope, owner, and uncertainty attached.
A blank answer, a machine guess, or a polished document must never look like a
human decision.

## Actors And Work

| Actor | What they do |
| --- | --- |
| Person doing the work | States the goal, answers questions, corrects guesses, and keeps important choices visible. |
| Machine collaborator | Finds possible sources, suggests concepts, shows conflicts, and checks that nothing required disappeared. |
| Work owner | Owns the goal or the next piece of work. |
| Definition owner | Owns an existing definition or the route for reviewing a new one. |
| Definition Pack receiver | Decides whether the pack is useful for one stated purpose and may accept it, question it, or send it back for clarification. |

One person may fill several roles. The roles still matter: helping with work,
owning a definition, and having permission to approve a change are different
things.

## Problems

Define handles practical failures such as:

- two teams use the same word differently;
- an important decision exists, but nobody can find its source;
- a polished document silently leaves out an unresolved concept;
- a definition is precise but no longer serves the original goal;
- the user must repeat context that is already visible;
- the machine treats its own guess as something the user said; or
- nobody knows who may settle a disputed meaning.

## Capabilities

Define must be able to:

1. take the user's goal, context, and references;
2. use relevant visible or saved context as clearly labeled suggestions;
3. ask for more context when the available material is not enough;
4. find the concepts the next stage needs;
5. show sources, conflicts, stale evidence, and missing evidence;
6. record one of the four choices for each concept;
7. check that every required concept is still present;
8. build a Definition Pack that a person can inspect; and
9. save, resume, refresh, and hand the work to its next receiver.

These are product requirements. The system ontology describes a possible
technical realization, but it does not prove that the product has been built.

## Outputs And Outcomes

The output is a **Definition Pack**. It contains the goal, intent, context,
required concepts, choices, sources, evidence, owners, relationships, and open
questions for one piece of work.

We want the pack to produce three changes:

- **Shared meaning** — people and tools use the same checked meaning.
- **A reviewable next step** — the receiver can understand, challenge, accept,
  defer, or reject what should happen next.
- **Continuity** — the next person, tool, or session can continue without
  repeating avoidable discovery.

A pack or passing validator does not prove that these changes happened. They
must be observed in real use.

## Business Rules

1. Every required concept gets one current choice or remains visibly open.
2. Every choice stays connected to the original goal and reason for the work.
3. Context supplied by the user comes before machine suggestions.
4. Context inferred from the current conversation or saved session is labeled
   as inferred so the user can correct or reject it.
5. When context is not enough—or it is unclear whether it is enough—Define asks
   whether the user wants to add more. Silence is not agreement.
6. Evidence, ownership, a user answer, a passing check, or a handoff does not by
   itself approve a definition or give permission to implement it.
7. Routine searching and checking should stay lightweight. A visible approval
   step is needed only when a real consequence changes.
8. Conflicts, stale sources, and open questions stay visible. Define must not
   hide them to make the pack look complete.

Here, **permission** means the right to make a particular change real. A useful
answer is not automatically permission.

## Value And Measures

Define is useful if the next person can continue with less confusion and less
repeated work while still being able to question the result.

We should test this with concrete questions:

- Can the receiver find the goal, evidence, owner, and open questions without
  the original chat?
- Can the receiver explain why each important concept has its current meaning?
- When a pack is returned, does it name one clear missing concept or conflict?
- How much context must be rebuilt after a handoff or restart?
- Are conflicting or stale sources found before Design relies on them?
- Does Define ask focused questions without hiding hard but important work?

No metric formula, baseline, target, or product-value claim has been approved.

## Boundaries

Define does not:

- change the CyberAlchemy product thesis;
- guarantee that it captured everything a person intended;
- present a machine guess as a user statement;
- approve or publish a definition;
- choose the product design, architecture, database, or interface;
- approve Design or authorize implementation;
- migrate or remove an external package;
- publish, release, or deploy anything; or
- prove that users are faster, happier, or more successful.

## Example

Return to the refund example.

The team supplies the refund goal and links to the order policy. Define finds
three uses of “customer”:

- checkout calls the buyer the customer;
- account settings call the account owner the customer; and
- delivery support calls the recipient the customer.

Define shows the conflict and asks which person the refund rule concerns. If
the evidence shows that refunds go only to the buyer, the team can specialize
“customer” to mean “buyer for this refund workflow.” The pack records that
scope, the source, and the definition owner.

If the policy is unclear or nobody owns the decision, Define keeps “customer”
open. Design can then ask for that exact clarification instead of guessing.

## Owners

- The **CyberAlchemy v2 product owner** owns the wider product thesis and the
  candidate meaning of Define.
- The **definitions-governance owner** owns the route for approving canonical
  definitions.
- The **Define runtime owner** owns the technical implementation, not the
  product meaning.
- The **Definition Pack receiver** decides whether the pack is useful for one
  stated purpose. That decision does not approve a definition or authorize the
  next implementation step.
- The **external package lifecycle owner** owns any future decision to migrate
  or retire external behavior.

This document can describe those responsibilities. It cannot appoint an owner
or give anyone permission.

## Claim Ceiling

This is a private candidate explanation of the Define product. It links Define
to CyberAlchemy, but it does not approve the document, prove that Define is
implemented, show measured product value, approve a definition, authorize
work, migrate an external package, publish, release, deploy, or cause any outside effect.
