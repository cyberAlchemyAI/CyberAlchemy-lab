# `EA-C1-CAUSAL-001`: unusual causal invention

Status: **draft, not released**. Family: causal explanation plus constraint-changing invention. Intended construct: analysis, creativity and ingenuity in an unfamiliar problem. [Role trace](role-business-trace.md) and [common case contract](README.md) apply. This example avoids the public elephant/fridge/jungle sequence and does not require biological trivia.

## Participant-visible question protocol

**Context.** A field team uses a sealed container that protects fragile samples on a long trip. In bench tests, a simple container survives drops and keeps temperature stable. In real shipments, some samples arrive damaged only after long trips. The outside has no visible damage. The team can change the container design or handling process, but added mass and complexity are costly. You have no specialist material-science data; reason from the facts given and identify what you would need to learn.

**Turn 1.** “Give at least two distinct explanations that fit these facts. What observation or low-cost test would distinguish them? Propose one useful change, and say what could make it fail.”

**Fixed reveal.** “A logger from several trips shows that damage is more common on trips with many small vibrations, including trips with no large impact. One container arrived undamaged after a large drop. The temperature trace remains normal.”

**Turn 2.** “Update your causal explanation and your best change. You may keep an earlier idea if you can justify it. What is one small test that could disprove your revised idea, and what would you try next if it fails?”

Answer budget: at most ten minutes recorded. The case is deliberately underdetermined; uncertainty and justified alternatives are part of the task. No exact scientific mechanism is assumed. A supported text/diagram response must preserve the same evidence opportunities. Before release, reviewers must confirm that the terms are understandable across the target population and that the reveal is informative without forcing one canonical answer.

## Reviewer-only mechanism and alternatives

The mechanism is **competing causal models updated by new evidence**, followed by a feasible intervention under cost constraints. Possible hypotheses include cumulative vibration/resonance, internal movement or packing relaxation, handling patterns correlated with trip length, or a sensor/measurement artifact. Defensible interventions include changing retention/packing geometry, damping, process checks or route/handling with a test that distinguishes a causal effect from correlation. A creative answer can reframe the unit of change (container, packing, transport process, monitoring) while respecting sample protection and cost. A candidate may reject all exemplar hypotheses with a better evidence-consistent model.

Invalid shortcuts include claiming the reveal proves one exact cause, treating the large drop anecdote as proof that impact can never matter, or proposing an expensive redesign without a test or failure condition. Reviewers must check that domain specialists do not rely on unstated knowledge to grade the item. This draft is not a scored question until an expert can document at least two valid response paths and a useful but non-obvious path from the stated facts.

## Dimension-level scoring opportunities

Use universal `0–4`, `NA` and `UNK` rules from [scoring-model.md](../scoring-model.md). `2` means plausible with a material gap, `3` specific and constraint-aware, `4` survives the reveal/counterargument and states residual risk. Count of ideas is recorded separately; `N` judges the best developed *useful* option.

| Dimension | Observable evidence | `2` example | `3` example | `4` example / `NA` condition |
| --- | --- | --- | --- | --- |
| `R` representation | Names goal, cost constraint, evidence and uncertainty; distinguishes observed damage from proposed mechanism. | States a plausible cause but treats it as fact. | Maps multiple causes to observations and constraints. | Reframes container/handling/measurement boundaries and explains what remains unknown; `NA` only if the case facts were not delivered. |
| `A` assumption/causal test | Identifies assumptions and a discriminating observation or test. | Suggests a test that would detect damage but not distinguish causes. | Proposes a feasible comparison that separates at least two models. | Predicts different outcomes under competing models and names a confound; `NA` only if the test probe was omitted. |
| `D` viable diversity | Offers meaningfully different explanation/intervention paths, each linked to a mechanism. | Two wordings of one idea or two paths with one infeasible. | Two distinct viable causal/intervention paths. | Several distinct paths with explicit conditions for choosing among them; `NA` only if alternatives were not requested. |
| `N` useful originality | Best developed intervention changes a mechanism or framing and could meet the goal. | Some novel element with uncertain use or fit. | A non-obvious, workable change tied to the evidence. | A useful reframe that survives the reveal and anticipates a limitation; `NA` only if invention was not requested. Familiarity and domain expertise are recorded as rivals, not score discounts. |
| `F` feasibility/evidence | Addresses mass/complexity, testing cost, sample protection and disconfirmation. | Plausible idea but no decisive feasibility check. | Bounded test and cost/failure consideration. | Test could falsify the preferred solution, with next step if it fails; `NA` only if no feasibility prompt was delivered. |
| `V` revision | Explicitly updates or defends the model after vibration evidence. | Mentions reveal but keeps plan without causal explanation. | Changes confidence, test or intervention consistently. | Explains why prior belief changed or held, preserves alternate cause and specifies residual uncertainty; `NA` if reveal not delivered. |

Do not reward a punchline, biological/material trivia, speaking speed or the largest number of ideas. Concise reasoning can reach the highest anchor. A novel answer that violates stated constraints cannot receive high `N` and `F` merely for rarity.

## E02/E03/E05A checks

- **Review/trial:** blind experts confirm underdetermination is productive rather than ambiguous, at least two defensible paths, no hidden domain fact, clear wording and answerability in ten minutes. Ask trial participants what facts they believed were given versus assumed.
- **Exposure/duplicates:** fingerprint “cumulative small stress despite surviving a large shock” as the underlying pattern. A new container story with the same pattern is not an independent family. Record candidate familiarity with analogous riddles.
- **Calibration:** compare blind expert judgment of the best developed idea with analytic `R/A/D/N/F/V` ratings, including concise and unusual-valid responses. Check raw/corrected transcript and supported text mode.
- **Transfer:** use an unseen engineering invention/debugging work sample in a different domain, blind rated for novelty, usefulness, feasibility and causal testing. Compare with a conventional reasoning task and control for prior exposure/experience.

If ratings primarily reflect jargon or prior knowledge, revise or retire the item. If one case does not generalize across families, report situated performance only.
