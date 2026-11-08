# Source Record

Target: Alloy and TLA+/PlusCal for DomainSpec v2 modeling.

Date checked: 2026-06-16

## Primary External Sources

| ID | Source | Version or freshness | URL | Source boundary | Use in tower |
| --- | --- | --- | --- | --- | --- |
| S1 | Alloy Tools homepage | Latest release listed as Alloy 6.2.0, release date 2025-01-09 | https://alloytools.org/ | primary-source | Tool identity, release freshness, Alloy 6 temporal note |
| S2 | Alloy Tools about page | checked 2026-06-16 | https://alloytools.org/about.html | primary-source | Alloy as language for evolving structures, Analyzer as solver for examples/counterexamples |
| S3 | Alloy Tools documentation page | checked 2026-06-16 | https://alloytools.org/documentation.html | primary-source | Alloy 6 jar, model finder, temporal model-checking dependency |
| S4 | Alloy FAQ: kind of analysis | checked 2026-06-16 | https://alloytools.org/faq/what_kind_of_analysis_does_the_alloy_analyzer_do.html | primary-source | Analyzer as model finder and counterexample search |
| S5 | Alloy command documentation | checked 2026-06-16 | https://alloy.readthedocs.io/en/latest/language/commands.html | related-source | `run`, `check`, bounded scopes, step scopes |
| S6 | Leslie Lamport TLA+ homepage | Last modified shown on page as 2025-05-14 for news | https://lamport.azurewebsites.net/tla/tla.html | primary-source | TLA+ learning/tool entry point |
| S7 | Leslie Lamport high-level TLA+ view | Last modified 2021-08-10 | https://lamport.azurewebsites.net/tla/high-level-view.html | primary-source | TLA+ as modeling above code, state-based behaviors, PlusCal entry |
| S8 | TLA+ tools GitHub repository | checked 2026-06-16 | https://github.com/tlaplus/tlaplus | primary-source | CLI tools, Java requirement, TLC, SANY, PlusCal translator |
| S9 | TLA+ Toolbox paper | checked 2026-06-16 | https://lamport.azurewebsites.net/pubs/toolbox.pdf | primary-source | TLC finite model checking, TLAPS deductive proof, PlusCal translation caveats |

## Local Sources

| ID | Source | Version or freshness | Path | Source boundary | Use in tower |
| --- | --- | --- | --- | --- | --- |
| L1 | DomainSpec taxonomy | current checkout | `arcanum/definitions/TAXONOMY.md` | local-source | Meta-concepts: Saga, Workflow, Operation, Rule, Policy, Event, State Machine, Interface, Mapping |
| L2 | DomainSpec relationships | current checkout | `arcanum/definitions/RELATIONSHIPS.md` | local-source | Typed edges and `orchestrates` residue |
| L3 | DCB saga model choice | 2026-06-15 | `projects/domainspec-v2/research/dcb-saga-correctness/MODEL-CHOICE.md` | local-source | TypeScript first, TLA+/PlusCal and Alloy promotion split |
| L4 | DCB saga synthesis | 2026-06-15 | `projects/domainspec-v2/research/dcb-saga-correctness/SYNTHESIS.md` | local-source | DCB as freshness wrapper, not proof engine |
| L5 | DCB saga proof obligations | 2026-06-15 | `projects/domainspec-v2/research/dcb-saga-correctness/PROOF-OBLIGATIONS.md` | local-source | Obligation classes and fact classification |
| L6 | Toy run result | 2026-06-16 | `projects/domainspec-v2/research/dcb-saga-correctness/toy-run-result.md` | local-source | Bounded witness result and graph residue |
| L7 | Two-lane discipline | 2026-06-11 | `projects/domainspec-v2/research/TWO-LANE-DISCIPLINE.md` | local-source | Lane Z / Lane A tower convention |
| L8 | `/domainspec-subagents-strategy` router | 2026-06-15 | `internal_tools/subagents-dispatch-hooks/skills/domainspec-subagents-strategy/SKILL.md` | local-source | Human gate and dispatch lifecycle |
| L9 | Research type skill | 2026-06-15 | `internal_tools/subagents-dispatch-hooks/skills/research/SKILL.md` | local-source | Research dispatch roles, findings shape, citation discipline |

## Source Boundary Notes

- Alloy source claims are about Alloy Tools and Alloy language behavior, not about Grafana Alloy.
- TLA+ source claims are about TLA+, PlusCal, TLC, TLAPS, and the TLA+ tools, not about implementation verification of generated code.
- Local bridge claims are DomainSpec operator readings and must be labeled `local-inference` or `operator-reading`.
- The example `.alloy` and `.tla` files are illustrative sketches until run through their tools.
