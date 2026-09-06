# Alloy And TLA Modeling Tower

Status: active
Date opened: 2026-06-16
Tower id: `domainspec-v2-alloy-tla-modeling`

## Underlying Problem

DomainSpec v2 needs a disciplined way to turn taxonomy and relationship artifacts into checkable correctness evidence without overclaiming that a local TypeScript witness, DCB read set, Alloy model, or TLA+ model is a complete proof by itself.

## Research Question

How can Alloy and TLA+/PlusCal be used in the DomainSpec v2 workflow, especially after the `OrderFulfillmentSaga` bounded witness exposed both relationship-graph residue and temporal saga obligations?

## Initial Hypothesis

Alloy and TLA+ are not interchangeable proof upgrades.

- Alloy should be used when the question is structural: "Is there a bounded counterexample to the DomainSpec concept or relationship graph?"
- TLA+/PlusCal should be used when the question is temporal: "Is there an execution trace that violates success safety, failure safety, compensation ordering, retry behavior, liveness, or freshness acceptance?"
- TypeScript should remain the first extraction and bounded-witness layer because it is already runnable in this repo and can emit data for both formal lanes.

## Local Evidence Base

The DCB saga correctness packet already decided that the first pilot is a TypeScript bounded witness, not a proof. It also recorded the promotion rule:

- promote to TLA+/PlusCal if temporal behavior is the hard class;
- promote to Alloy if relationship graph completeness is the hard class;
- keep DCB on freshness and acceptance, not behavioral proof.

Local anchors:

- `projects/domainspec-v2/research/dcb-saga-correctness/MODEL-CHOICE.md`
- `projects/domainspec-v2/research/dcb-saga-correctness/SYNTHESIS.md`
- `projects/domainspec-v2/research/dcb-saga-correctness/PROOF-OBLIGATIONS.md`
- `projects/domainspec-v2/research/dcb-saga-correctness/toy-run-result.md`

## Lane Z: Formal Promotion Build-Out

Lane Z takes the local DCB saga witness as given and asks how to promote it into a formal surface.

### Z1: Alloy Graph Lane

Question: Can a bounded Alloy model find missing DomainSpec edges, missing compensation links, orphan participants, or strained relationship signatures?

Expected output:

- an Alloy signature shape for Saga, Participant, Operation, Policy, Event, State Machine, Interface, Mapping, and typed edges;
- assertions for "every forward operation has compensation or terminal policy";
- counterexamples for missing compensation or missing cross-context activation.

Bridge decision: promotion-candidate for graph completeness checks.

### Z2: TLA+/PlusCal Temporal Lane

Question: Can a small TLA+/PlusCal model express the saga as a state-machine behavior and check safety or liveness obligations over bounded execution models?

Expected output:

- Init and Next actions for saga state;
- invariants for success safety and failure safety;
- optional liveness/fairness for retry or eventual terminal state;
- a freshness rejection action around proof/evidence acceptance.

Bridge decision: promotion-candidate for saga execution behavior.

## Lane A: Alternatives And Skeptic Lane

Lane A holds the problem fixed and challenges the formal-tool choice.

Alternatives:

- Keep TypeScript bounded witness plus property tests if the result only needs quick repo-local feedback.
- Use content hashes, rerun-before-use, or certificate binding for deterministic facts before adding DCB or formal model overhead.
- Defer Lean until there is a stable theorem small enough to justify theorem-prover work.

Bridge decision: borrow-carefully.

## `/domainspec-subagents-strategy` Use

This tower includes a proposed research dispatch in `subagents/PROPOSED-DISPATCH.md`.

The strategy is not registered or run in this task because `/domainspec-subagents-strategy` requires a proposed sheet, a tension gate, and explicit human confirmation before actual fan-out or ledger append. This tower records the lanes and a not-used closeout instead of pretending subagents ran.

## Completion Boundary

This tower closes the feasibility research layer enough to guide the next task. It does not close:

- Alloy syntax or Analyzer validation;
- TLA+ syntax, PlusCal translation, or TLC validation;
- integration into DomainSpec validators;
- promotion into a canonical proof workflow.
