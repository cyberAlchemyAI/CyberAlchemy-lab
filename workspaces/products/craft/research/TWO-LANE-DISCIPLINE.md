# The Two-Lane Discipline

Status: discipline (project convention for DomainSpec v2)
Date: 2026-06-11

Every DomainSpec v2 research tower runs two lanes in tension and only closes
after a synthesis adjudicates them. The point is to stop us from elaborating the
first idea into a foregone conclusion.

## Lane Z — Zig-Zag (explore the idea)

Lane Z takes the hypothesis as given and **builds it out by alternating
generation and critique** (`zig_zag`). Generate a concrete version of the idea,
attack it with its own strongest counterexample, adjust, repeat. Lane Z's job is
not to defend the idea — it is to find where the idea actually holds and where it
breaks under its own weight.

A Lane Z pass is honest only if it ran the idea into at least one real
counterexample, not just a friendly demo.

## Lane A — Alternatives (challenge the problem, not the idea)

Lane A **holds the underlying problem fixed and proposes a genuinely different
solution**. It is not allowed to produce a variant of Lane Z's idea. If Lane Z
unifies spec and ontology, Lane A might keep them separate behind a generated
bidirectional mapping. If Lane Z adopts NDD narratives as the target state, Lane
A might use fitness functions or acceptance-criteria goal-trees.

Lane A exists because the most expensive failure mode is anchoring: shipping the
first framing because nobody was assigned to disagree with it.

## Stating the underlying problem

Each tower SEED must write the **underlying problem** as a one-sentence
problem statement that is independent of the proposed solution. Both lanes are
measured against that statement, not against the hypothesis. This is the
formalization of "target-state thinking" applied to the research itself: name
the gap before naming the fix.

## Synthesis (adjudication)

A tower closes only when a synthesis:

1. Names what problem each lane actually solved vs. only reframed.
2. Issues a bridge decision per claim: `borrow-carefully`, `analogy-only`,
   `block`, `promotion-candidate`, or `future-work`.
3. Records residue with an owner.

Bridge decisions are local. Promotion into a DomainSpec template, validator,
ontology, or runtime contract requires a separate approved `task-session`.

## Why two lanes and not three

Two lanes is the minimum that creates real tension (advocate vs. alternative)
while staying joinable by one parent synthesis. Add a third lane only when a
tower has a distinct second alternative worth its own owner; otherwise fold it
into Lane A as a named candidate.
