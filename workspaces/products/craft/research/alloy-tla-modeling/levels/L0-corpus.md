# L0 Corpus

Status: pass

## Corpus Purpose

This level identifies the smallest source set needed to reason about Alloy and TLA+ for DomainSpec v2 without drifting into a general formal methods survey.

## External Corpus

| Source | Reason included | Used for | Boundary |
| --- | --- | --- | --- |
| Alloy Tools homepage | Tool identity and current release signal | Alloy capability and release freshness | official source |
| Alloy Tools about page | Plain description of Alloy models and Analyzer | Structural modeling and counterexamples | official source |
| Alloy Tools documentation page | Alloy 6 runtime/download and temporal note | Tool setup and temporal dependency caution | official source |
| Alloy FAQ analysis page | Model finder/counterexample mechanism | Claim C2 | official source |
| Alloy command docs | `run`, `check`, scopes, steps | Bounded result semantics | related source |
| Lamport TLA+ homepage | Official TLA+ entry point | Tool landscape | official source |
| Lamport high-level TLA+ view | TLA+ and PlusCal conceptual model | State behavior and PlusCal entry | official source |
| TLA+ tools GitHub | CLI tooling and Java requirement | future validation task | official source |
| TLA+ Toolbox paper | TLC/TLAPS distinction and PlusCal translation caveats | proof-label guardrail | official source |

## Local Corpus

| Source | Reason included | Used for | Boundary |
| --- | --- | --- | --- |
| `TAXONOMY.md` | DomainSpec meta-concepts | model vocabulary | explanatory layer; canonical definitions elsewhere |
| `RELATIONSHIPS.md` | DomainSpec edge signatures | graph completeness lane | explanatory layer; canonical definitions elsewhere |
| DCB saga correctness packet | Existing decision and toy witness | operator bridge | local research |
| Two-lane discipline | v2 tower convention | Lane Z / Lane A | project convention |
| `/domainspec-subagents-strategy` router | subagent governance | proposed dispatch, no hidden fan-out | local governance |

## Excluded Corpus

| Source | Reason excluded |
| --- | --- |
| Broad blog posts about TLA+ or Alloy | not needed for first source-backed tower |
| Grafana Alloy docs | different product named Alloy |
| Lean material | deferred until theorem is narrow |
| Production case studies | useful later, not needed to choose the first lane |
