## CAV2-D61: Research

Status: active
Term: research
Aliases: governed research, project research, research aggregate
Promoted: 2026-08-29 by owner-requested product-foundation modeling; definition authority only

### Normative Definition

Research is a bounded, attributable investigation that gathers and organizes
source material and observations to answer one declared question for a Project
and one or more Goals.

A Research artifact must preserve its question, scope, sources, method,
evidence aggregate, counterevidence, limitations, owner route, Goal and Project
links, and references to any separate findings. Research records what was
investigated and gathered. It does not silently turn its evidence aggregate
into a conclusion, decision, definition, specification, or product claim.

### Formal Interpretation

```text
Research =
  (id, project_ref, goal_refs, question, scope, sources, method,
   evidence_aggregate, counterevidence, findings_refs, limitations,
   created, last_updated, owner_route, challenge_route)

Research.outcome is absent
Findings.question = Research.question
Findings derives_from Research
```

### Schema

Schema handle: `CAV2-D61-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary).
The machine-checkable private record and Markdown carrier checks live under
[../../research/](../../research/README.md).

### Operational Interpretation

Use Research when a Project must inspect literature, repositories, benchmarks,
past evidence, observations, or competing explanations before deciding what to
believe or do. Keep the aggregate separate from findings so a later reader can
see the source material without inheriting the synthesis as fact.

### Plain-Language Intuition

Research is the evidence-gathering investigation behind an answer. It shows the
question, what was examined, how it was examined, and what remains uncertain.

### Domain-Context Voice

In CyberAlchemy v2, the PythonConstraint Research record explains why that
benchmark was selected, which exact sources support the selection, and which
questions about DomainSpec-v2 fit remain open. It informs the Project and Goal
without claiming that the experiment has run.

### Boundary

Research is not a Goal (`CAV2-D59`), Project (`CAV2-D60`), experiment
(`CAV2-D62`), findings, owner decision, canonical definition, proof, or
execution authority. It is an ephemeral canonical Evidence artifact: it records
an investigation at a time and cannot become authority by promotion.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [../../research/README.md](../../research/README.md)
- [../../research/RESEARCH-DOCUMENT-TYPE.md](../../research/RESEARCH-DOCUMENT-TYPE.md)
- [../../goals/README.md](../../goals/README.md)
