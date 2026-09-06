# D65 DomainSpec source admission

Status: selected
Decision: `CAL-D65SRC-0019`
Selected option: `D65SRC-1`
Resolved gate: `G-D65-DOMAINSPEC-SOURCE`
Next gate: `G-D65-COMPILE`

The DomainSpec v2 source and profile owners admitted the exact validated D65-S4 authored-source candidate for integration epoch 001. The admitted source maps all business subjects, relations, contracts, and failures and defines the event-sourced node/relation snapshot and governed projection contracts.

The exact development-only profile binding is admitted only for this source epoch; it is not released or generally admitted. No compiled graph or system ontology was materialized or admitted. D65-S5 becomes eligible for separate bounded construction and validation at `G-D65-COMPILE`.

No implementation binding, Rust mutation, migration, cutover, publication, release, deployment, or external effect is authorized.
