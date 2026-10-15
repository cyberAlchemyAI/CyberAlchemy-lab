# Lab artifact storage architecture

Status: **proposed**, 2026-10-07. Authority effect: **none**. No existing source, admitted package, runtime store or database is migrated by this proposal.

## Recommendation

Reuse the **event-sourced transaction pattern** already implemented for ontology and Lab runtime. Keep exact committed content/history in immutable canonical packages; use **SQLite as a rebuildable artifact read model**; materialize individual files selectively for authoring, review, export and code consumption.

Current authored and admitted repository files retain their existing authority. Compact packages are a proposed format for selected future operational volume, with an explicit source-profile/migration boundary. Generated files and SQLite rows have no independent admission authority.

Event sourcing is the history model. SQLite is a persistence/query engine. They are independent choices: a future canonical SQLite event store is technically possible, but it changes custody, recovery and collaboration assumptions and is not required to adopt SQL queries now.

## Read in this order

1. [Option comparison](COMPARISON.md): current implementation facts, tradeoffs and conditions for canonical SQLite.
2. [Architecture](ARCHITECTURE.md): writing, reading, ontology integration, exact bytes and file generation.
3. [Schemas](SCHEMAS.md): four proposed storage protocol schemas and a draft SQLite DDL.
4. [Independent review](REVIEW.md), [source baseline](SOURCE-BASELINE.json) and [schema authoring evidence](receipts/schema-authoring.json).

The protocols here are candidate implementation schemas, **not newly admitted Artifact Types**. Existing domain schemas remain selected by their exact carriers. Future workflow/action/profile protocols remain a separate specification layer.

## Connection to the roadmap

This supplies a design input for C01/C02/C07/C08, S01/S02, O01/O02/O03 and R02/R03 of the [integrated roadmap](../../plans/0009-lab-integrated-roadmap/PLAN.md) and its [single-checkpoint variant](../../plans/0009-lab-integrated-roadmap/single-checkpoint/PLAN.md). The original roadmap and its frozen source baseline are preserved; this proposal does not mark tasks complete or authorize their execution.
