# Declarative pricing construction

Status: local prototype construction; user authorized plan and implementation, 2026-09-05. No operational authority.

## Definitions and ontology scaffold

Reuse Mapping for typed shape transformation, Rule for boolean predicates, Query for read-only collection/result selection, Calculation for exact arithmetic, and Interface for the HTTP boundary. A query composition is a contract extension, not a new meta-type. Derived declaration dependencies are compiler references, not invented ontology relationship kinds. No Rule-enforces-Query edge is emitted.

Product prototype: given a validated request and bounded price snapshot, return no_price, ambiguous_price, or quoted with exact cents and subtotal. Business prototype: match currency and inclusive quantity bands, ignore deleted/nonmatching rows, choose the least unit amount, expose ties, reject unsupported pricing features and overflow. Preserve predecessor fixtures and boundary failures.

DomainSpec prototype: an opt-in, typed declaration graph with computed Mapping fields, finite collection Query selection, quantified Rule expressions, and mutually exclusive Query result cases. Compiled-system prototype: deterministic JavaScript module plus typed contract and declaration/dependency trace. Implementation prototype: Alch parser and lowering call the DomainSpec public generator; a transport-only boundary validates and fetches inputs, then calls generated code. No procedural flow evaluator in the new artifact.

## Product construction lane

Frontier at start: existing-type fit established; composition and exact numeric realization missing.

1. Define a bounded expression/type algebra and graph contracts; reject unknown keys, unresolved references, cycles, invalid field access and type mismatches.
2. Generate exact bigint code under DomainSpec ownership for transformations, quantifiers and result construction; reuse existing exact Calculation generation.
3. Add declarative Alch syntax and lower its declarations into that contract. Keep integration and endpoint declarations in the same file.
4. Compile the pricing candidate; test all predecessor fixtures, adversarial boundaries, source-driven behavior, and deterministic generation.
5. Capture exact candidate hashes and current test evidence. Product approval remains an owner decision after the candidate is testable.

Runnable work: all five local prototype stages, in dependency order. Causal blockers: none at start; failures in type checking or executable parity must be repaired before candidate completion.

## Operational support lane

No operational task is prerequisite for this local construction. Deployment/publication are deferred residue owned by their respective release/deployment owner, affecting only release/deployment stages. No credentials, remote provider calls, registry admission, commit or push are part of this work. Meta-Type Factory automation remains deferred in ../current-meta-type-fit-v1/FUTURE-DEVELOPMENT.md.

## Open questions

How should the new composition contract enter the broader DomainSpec project-graph certification surface? This prototype emits a separate explicit contract and dependency trace; it must not be presented as ontology admission or full project certification. Other language targets and hosting providers are future realization work.
