---
example_id: ARE-INTERACTION-EXAMPLE-APPROVED-FORMAT-001
status: user-directed-design-example
route_id: CA2-ROUTE-PLAN
work_lane: product-construction
affected_stage: interaction-learning design and benchmark specification
authority_effect: none
---

# Learn and reuse an explicitly approved explanation format

## User evidence

In this conversation, the user supplied a compact arrow diagram of the work,
learning, and research loops and said:

> this explanation is go, set this as example of optimization that we should look for, when user approves or ask for a specific time of demonstration, we should repeat it

Interpretation in context: reuse the approved **type** of demonstration for
similar explanations. The word "time" does not establish a schedule or reminder.
The approval concerns presentation, not factual correctness, implementation
completion, or permission for effects.

## Whole-engine product view

```text
Request + reusable reasoning state
                 |
                 v
Interpret -> route -> assemble context -> check permission -> act
   ^                                                         |
   |                                                         v
   |                                                      observe
   |                                                         |
   |                                                         v
   |                                                      assess
   |                                                         |
   +--- next permitted step <--- continue / ask / finish ------+

Assessment + user feedback
          |
          v
Reflect -> scoped lesson -> apply when relevant -> measure application
                ^                                        |
                +---- revise / suspend <--- counterevidence+
                                                         |
                                                         v
                                                 reusable reasoning state

Recurring weakness / no gain / explicit improvement request
          |
          v
Hypothesis -> research -> experiment -> compare with baseline
                                           |
                                           v
                              retain / revise / reject
                                           |
                                           v
                                measured feedback
                                           |
                                           v
                            next improvement cycle
```

This is the whole-engine product view, not a claim that every connection is
implemented. The [interaction-learning plan](PLAN.md) describes the outstanding
integration. The [architecture](../../design/ARCHITECTURE.md) explains semantic
evaluation and effect boundaries; its historical maturity statements must not
be read as a fresh runtime assessment.

- Interpret resolves objective, references, corrections, and scoped preferences.
- Route selects the relevant capability and effort; not every request needs a Goal.
- Assemble context selects definitions, ontology meanings, constraints, current
  evidence and applicable lessons into a bounded frozen Context Envelope.
- Check permission protects the exact action. Act uses the selected tool, model,
  or orchestrator; orchestration does not own semantic judgment.
- Observe records outputs, failures, user feedback and available checks. Assess
  distinguishes task outcome, applicable semantic judgment/Reasoning Receipt,
  consequence and continuation. Unknown outcomes remain unknown.
- Continue takes an already permitted next step; ask exposes a real missing
  decision; finish stops completed work. A recommendation never grants effects.
- Append-only events, immutable epochs, provenance and selected-source freshness
  support these loops. Recovery reconstructs explicit state, not hidden model
  reasoning. Stable projections can improve caching, but cache hits do not prove
  freshness. Compaction must preserve load-bearing state.
- Inspection and control span every loop: why an interpretation or lesson was
  selected, its source, scope, currentness, results, and how to override it.
- Experiments produce measured candidates. Retaining an experiment does not
  automatically upgrade the serving engine.

## Scoped lesson

For this user's system/process explanations, prefer a compact arrow diagram
that shows the operating loop and feedback paths, followed by short plain-language
explanations. Preserve causal structure and boundaries rather than repeating
identical words. Apply without asking again on an obviously similar request.

An explicit current format request takes precedence. Do not infer a permanent
global preference from a one-off format request; persistence requires expressed
scope or retention permission. Here, the user explicitly asked to preserve the
example and repeat the format. Do not apply it to unrelated answers or add
internal labels to user-facing product artifacts.

The user can inspect, narrow, override, or revoke the lesson. A later correction
updates its scope; it must not force repeated confirmation of an unchanged,
applicable presentation preference.

## Proposed benchmark cases

1. Explicit approval plus request to reuse: record this format with its source
   and scope; show an arrow diagram on the next similar explanation request.
2. One-off "show this as a diagram": satisfy now without manufacturing a durable
   preference for every future task.
3. Current "use prose only" instruction: override the prior diagram preference.
4. Unrelated short factual question: do not force a process diagram.
5. Changed system architecture: preserve the explanation pattern while updating
   its content; never repeat obsolete edges just to match the old diagram.
6. Revocation or disabled retention: exclude the preference from subsequent
   selection and recovered projections according to the existing control policy.
7. Explicit diagram praise without correctness evidence: record presentation
   support, not successful task completion or a measured engine improvement.

Measure applicable-format adherence, inappropriate reuse, override/revocation
compliance, and additional formatting corrections. Actual later feedback is
application evidence; lack of complaint is not success. Controlled comparisons
are needed before claiming general improvement. These cases have not been run.

## Frontier and residue

Product construction: this example is ready to become a fixture in the existing
interaction-learning benchmark plan. No new preference service is proposed.
Operational support: the parent recorded the example; no runtime, deployment,
dispatch ledger, or frozen review target was changed. Automatic selection,
recovery and scoring remain implementation/test work in the existing plan.

## Open Questions

- What cross-conversation retention scope should the eventual user control
  profile expose? This repository example does not configure global memory.
- Which baseline and minimum useful gain will the implementation benchmark use
  for reduction in formatting corrections?
