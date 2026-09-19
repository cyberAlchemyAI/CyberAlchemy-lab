# CyberAlchemy v2 Bounded Composite Work

Status: candidate model-first package
Visibility: private
Package owner: CyberAlchemy v2 work-orchestration capability owner
Authority effect: none

This owner-local package contains exactly one Product Capability candidate:
`CA2-CAP-EXECUTE-BOUNDED-COMPOSITE-WORK`.

The capability lets CyberAlchemy describe finite or explicitly bounded work as
typed, composable units while preserving one root execution authority, explicit
input and output contracts, deterministic structural replay, and separate
domain and effect decisions.

The source RWO design is supporting proposal evidence for a possible later
realization. It is not the Product Capability, an adopted architecture, a
runtime, or proof that the capability works.

## Package boundary

This package materializes only the first three `CAV2-D65` stages:

```text
canonical definition references
  -> one Product Capability candidate
  -> one capability-local business ontology
```

It deliberately contains no DomainSpec project, compiled graph, system
ontology, RWO runtime, scheduler, journal implementation, adapter, conformance
claim, publication, release, deployment, or external effect.

## Capability boundary

The capability owns the product outcome: bounded composite work can be
described, routed, observed, and replayed without inheriting authority or
manufacturing domain truth.

It does not own:

- business or governance decisions;
- agent selection, prompting, tools, credentials, or communication permission;
- data quality, artifact meaning, or generation acceptance;
- retry, cancellation, compensation, or timeout policy;
- external-effect authorization;
- the authoritative state of a leaf operation; or
- unbounded or dynamically expanding computation.

ETL stages, agent invocations, data processors, generators, human decisions,
and validators may later appear as typed work adapters or domain gates. Their
meaning and authority remain with their own capability owners.

## Package map

- `profile.json` — one-capability package identity and construction ceiling.
- `sources.json` — exact source selections and digests.
- `definitions.json` — canonical references and package-local candidate terms.
- `product-capability.json` — the stable product outcome candidate.
- `product-capability-support.json` — unselected realization and obligations.
- `nodes.json` and `relations.json` — the business-domain ontology.
- `residue.json` — decisions and later stages that remain open.
- `schemas/work-orchestration.schema.json` — closed package schemas.
- `scripts/validate.py` — deterministic, check-only validator.
- `tests/test_negative_mutations.py` — fail-closed mutation checks.

## Validate

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 cyberAlchemy-v2/work-orchestration/scripts/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 cyberAlchemy-v2/work-orchestration/tests/test_negative_mutations.py
```

A PASS proves only the current candidate package shape, source currency,
single-capability boundary, business-graph closure, and authority-effect ceiling.
It does not adopt the capability or select, implement, or validate RWO.
