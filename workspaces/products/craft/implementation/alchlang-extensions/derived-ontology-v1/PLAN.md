# Derived ontology prototype

User-authorized product construction, 2026-09-05. Scope: declarative-function-v1 Alch ontology elaboration, inspection, and an unchanged pricing behavior expressed with fewer annotations.

## Definitions and construction stages

Reuse existing declaration meanings. The derived ontology is a source-linked structural scaffold, not a registry admission. Stable identity derives from domain, declaration kind and a key that defaults to its name. An explicit key preserves identity across a declaration rename. Authored descriptions remain authored; generated descriptions state structure only. Entity identity is derived only from one required identifier, otherwise an explicit identity annotation is required.

Product/business prototype: let authors describe the pricing behavior once, retain meaningful business descriptions, and inspect its ontology and dependencies. DomainSpec prototype: elaborate missing bindings before the established typed-contract validation. Compiled-system prototype: emit ontology.json alongside the generated behavior from that same validated model. Implementation: elaborate, validate, derive, inspect/explain, then test an exact candidate.

## Product construction lane

Initial frontier: declarative pricing passes tests; ontology blocks are still manually duplicated. Runnable stages: implement deterministic derivation and explicit overrides, expose ontology/explain CLI commands, verify provenance and rename behavior, then confirm all pricing fixtures and regression tests. No causal construction blocker at entry.

## Operational support lane

No operational task blocks construction. Registry admission, composition certification, publication and deployment remain deferred to their respective owners and stages. Generated ontology cannot authorize these effects. Prior frozen candidate artifacts remain historical and unchanged; this extension receives fresh evidence. Meta-Type Factory automation remains deferred.

## Open questions

Property renames and domain moves currently change derived identity; pinning an explicit ontology ID preserves a declaration across a domain move. Property identity follows its parent ID and current field name, matching the existing DomainSpec contract. A future migration mechanism would be needed for property aliases. Explanations in this slice concern static source semantics, not invocation outcomes or inferred business rationale.

## Current frontier

Implementation and local product tests complete: 105 Alch tests passed, typecheck passed, all 20 pricing fixtures passed again against the final bundle. The generated artifact and read-only CLI ontology match. Candidate product approval remains pending owner review; no operational effect has been performed.
