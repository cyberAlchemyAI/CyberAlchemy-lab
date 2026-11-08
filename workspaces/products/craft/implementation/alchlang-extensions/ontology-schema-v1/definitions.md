# Candidate definitions

| Term | Agent definition | Plain meaning | Constraint |
|---|---|---|---|
| Typed host ontology | Source-bound record properties, state ownership, operation and mapping relationships | One typed description drives generated artifacts | Exact source and property identities; no invented business meaning |
| Derived schema | A mechanical projection of typed ontology properties and mapping coverage | Validate facts and stored state without reauthoring fields | Opaque records stay opaque; type or identity ambiguity fails |
| Prepared migration | An immutable ontology difference bound to target artifact and the selected baseline epoch | Review the computed change before selecting it | A changed baseline or artifact invalidates the plan |
| Authored default | A literal scalar value declared on a property | Decide what existing records receive | Explicit business choice, never inferred |

These are prototype terms and navigation scaffolds. Open questions: [README](README.md#open-questions).
