# D65-S4 DomainSpec source candidate

This package translates the admitted CyberAlchemy capability-local business ontology into DomainSpec v2 authored source. It represents the business subjects one-to-one, adds the operations, calculations, events, policies, rules, and workflows needed to express event-calculated projections, and binds the separate DomainSpec Event Sourcing Contract.

The canonical truth is the event history. Each entity and relation has distinct semantic and governance streams. Events carry complete resulting state. `LatestNodeSnapshot` and `LatestRelationSnapshot` calculate current subject state at an exact global commit-position cut. `GovernedOntologyProjection` combines those snapshots only after exact, fail-closed governance joins.

## Important boundary

The local DomainSpec profile is explicitly development-only. The minted compiler is used twice in memory to verify deterministic graph and source-manifest bytes, but this package does not materialize either output. It also does not create a system ontology. Those are D65-S5 concerns after source-owner admission.

The admitted business relation vocabulary is richer than the active DomainSpec relationship registry. Canonical executable edges use only active registry verbs. Every business relation remains explicit in `mappings/business-to-domainspec.json`, with no false claim that it is equivalent to a compiler edge.

## Validate

Run:

```bash
python3 validate.py
```

A PASS is candidate evidence only. Admission remains an owner decision at `G-D65-DOMAINSPEC-SOURCE`.
