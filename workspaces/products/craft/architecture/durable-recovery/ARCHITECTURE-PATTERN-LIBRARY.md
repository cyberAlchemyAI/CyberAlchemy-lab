# Durable Recovery Pattern Library

Load only the card needed for the current implementation question.

| Concern | Read |
| --- | --- |
| Component boundaries and invariants | [`pattern-library/ARCHITECTURE-FOUNDATIONS.md`](pattern-library/ARCHITECTURE-FOUNDATIONS.md) |
| Allowed dependency direction and forbidden authority flow | [`pattern-library/DEPENDENCY-RULES.md`](pattern-library/DEPENDENCY-RULES.md) |
| Tests required for each durable property | [`pattern-library/TESTING-ALIGNMENT.md`](pattern-library/TESTING-ALIGNMENT.md) |
| Events, metrics, and evidence boundaries | [`pattern-library/OBSERVABILITY-ALIGNMENT.md`](pattern-library/OBSERVABILITY-ALIGNMENT.md) |
| Machine component cards | [`concepts.json`](concepts.json) |
| Machine relationship cards | [`relations.json`](relations.json) |
| Typed properties and profile constraints | [`properties.json`](properties.json), [`constraints.json`](constraints.json) |
| Current evidence findings | [`findings.json`](findings.json) |

The patterns are DomainSpec-local. Their logical contracts are portable; their current source observations are
TypeScript-specific and must not be generalized to Python, Rust, or production runtime evidence.
