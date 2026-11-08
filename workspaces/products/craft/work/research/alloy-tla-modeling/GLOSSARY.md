# Glossary

## Alloy

- Source kind: primary-source
- Local meaning: A language and Analyzer for modeling software structures as relational constraints and finding examples or counterexamples within a scope.
- Arcanum reading: Use it as a bounded relationship-graph witness engine for DomainSpec.
- Promotion status: promotion-candidate
- Misuse warning: Do not treat one bounded Alloy pass as an unbounded proof.
- Evidence: S1-S5 in `SOURCE-RECORD.md`

## TLA+

- Source kind: primary-source
- Local meaning: A mathematical language for state-based models above code level, with tools such as TLC and TLAPS.
- Arcanum reading: Use it to model saga behaviors as possible executions over state variables.
- Promotion status: promotion-candidate
- Misuse warning: Do not collapse TLC model checking and TLAPS theorem proving into one "proof" label.
- Evidence: S6-S9 in `SOURCE-RECORD.md`

## PlusCal

- Source kind: primary-source
- Local meaning: A pseudocode-like language for algorithms, especially concurrent or distributed ones, translated into TLA+.
- Arcanum reading: Use it as the first authoring surface when a TLA+ model would otherwise be too notation-heavy for operators.
- Promotion status: borrow-carefully
- Misuse warning: Do not assume PlusCal can express every refinement or fairness condition that direct TLA+ can express.
- Evidence: S7, S9 in `SOURCE-RECORD.md`

## TLC

- Source kind: primary-source
- Local meaning: The TLA+ model checker for executable finite models.
- Arcanum reading: Use TLC as a validation gate over a bounded temporal model.
- Promotion status: promotion-candidate
- Misuse warning: Do not call TLC output an infinite-state theorem proof.
- Evidence: S7-S9 in `SOURCE-RECORD.md`

## TLAPS

- Source kind: primary-source
- Local meaning: The TLA+ proof system for deductive reasoning about specifications.
- Arcanum reading: A later proof lane after a TLA+ theorem is stable and worth proving.
- Promotion status: future-work
- Misuse warning: Do not include TLAPS in the first feasibility path unless the theorem is already small.
- Evidence: S6, S9 in `SOURCE-RECORD.md`

## Bounded Counterexample

- Source kind: operator-reading
- Local meaning: A model found within an explicit finite scope that violates an assertion.
- Arcanum reading: The strongest first result Alloy should contribute to graph completeness work.
- Promotion status: promotion-candidate
- Misuse warning: Do not infer absence of all bugs from absence of bounded counterexamples.
- Evidence: C3 in `CLAIM-LEDGER.md`

## Temporal Saga Behavior

- Source kind: local-inference
- Local meaning: The class of saga obligations involving execution order, compensation, retry, timeout, dead-letter behavior, state transitions, and acceptance freshness.
- Arcanum reading: The first formal target for TLA+/PlusCal.
- Promotion status: promotion-candidate
- Misuse warning: Do not ask Alloy's static graph model to carry this unless the model explicitly uses Alloy 6 temporal features and the tradeoff is justified.
- Evidence: L3-L6 in `SOURCE-RECORD.md`

## Graph Completeness

- Source kind: local-inference
- Local meaning: The class of obligations requiring all participants, operations, compensations, policies, interfaces, mappings, and typed relationships to be represented.
- Arcanum reading: The first formal target for Alloy.
- Promotion status: promotion-candidate
- Misuse warning: Do not claim graph completeness proves temporal saga correctness.
- Evidence: L1, L2, L5, L6 in `SOURCE-RECORD.md`

## Freshness Acceptance

- Source kind: local-inference
- Local meaning: The DCB-side condition that a proof verdict, model run, waiver, or receipt can be accepted only if its read facts have not changed in relevant ways.
- Arcanum reading: The boundary where DCB remains valuable after a formal model result exists.
- Promotion status: borrow-carefully
- Misuse warning: Do not turn DCB into the behavioral proof engine.
- Evidence: L4-L6 in `SOURCE-RECORD.md`
