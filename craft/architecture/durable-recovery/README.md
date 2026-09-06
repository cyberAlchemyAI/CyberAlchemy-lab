# Durable Recovery Architecture

Status: canonical design, partially implemented

Architecture ID: `domainspec-durable-recovery@2`

Ontology type: `architecture-property`

Owner: DomainSpec v2 owner

Visibility: private

This package defines the logical architecture that realizes DomainSpec Workflow Compensation without choosing
a database, ORM, message broker, clock library, or deployment topology. It separates the currently observed
TypeScript, Python, and Rust in-process planner/executor profiles and generated-target surface from the designed
durable coordination machinery. Version `@2` supersedes
`@1` by replacing its universal `Port` element with concern-specific dependency contracts and explicit
Persistence, Transaction Guarantee, Failure Outcome, and Durable Workflow Runtime bindings.

That successor design is provenance-bound to the infrastructure-binding Research Tower, System Integration
Contract Layer Revision 2, and the explicit owner admission. The research records have no authority effect;
the admission selects the D45-D49 distinctions and this architecture. The provider-neutral
`impl/system-integration/` package now implements closed binding schemas, profile and reference validation,
deterministic TypeScript/Python/Rust contract generation, CLI receipt binding, and exact static observation.
No provider or runtime is selected, and `runtime_guarantees_observed` remains false.

The machine JSON files are the architecture-property ontology. Markdown files are selective human views.
Neither surface proves that a designed component is implemented.

## Start here

1. [`ARCHITECTURE.md`](ARCHITECTURE.md) — logical components, control flow, state ownership, and implementation boundary.
2. [`ARCHITECTURE-PATTERN-LIBRARY.md`](ARCHITECTURE-PATTERN-LIBRARY.md) — selective pattern index.
3. [`profile.json`](profile.json) — package identity, claim ceiling, and processing guarantee.
4. [`properties.json`](properties.json) — typed architecture properties.
5. [`constraints.json`](constraints.json) — the portable durable-recovery profile.
6. [`findings.json`](findings.json) — observed, partial, and unsupported implementation facts.
7. [`residue.json`](residue.json) — unresolved technology and production-adapter choices.

## Validation

Run under the repository Node 26 environment:

```text
node validate.mjs --require-receipt
```

The validator checks source currency, three-profile implementation evidence, closed record shapes, stable
identities, the research-to-owner-admission chain, relation endpoint closure, property and constraint references, finding completeness,
unknown-evidence preservation, residue bindings, and the latest append-only receipt.
