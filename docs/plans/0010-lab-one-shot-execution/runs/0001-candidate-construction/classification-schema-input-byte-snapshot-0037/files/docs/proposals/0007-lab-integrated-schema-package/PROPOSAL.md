# Integrated Lab schema package

Status: **candidate; no admission or runtime effect**. Scope: the selected local Agent–Lab model and its future implementation boundary.

This package produces the message contracts needed to connect the existing Lab artifact model with ephemeral Agents, local services, review/admission, workflows, ontology representations, SQLite queries and generated files. It reuses current domain contracts and the prior storage proposal.

## What is included

| Surface | Coverage |
|---|---:|
| New candidate protocol schemas | 80 |
| Registered domain contract versions bound exactly | 143 |
| Current domain carriers eligible for current-write evaluation | 121 |
| Historical carrier versions retained for reading | 22 |
| Existing Relation Kinds / exact declared endpoint pairs | 41 / 550 |
| Reused candidate storage JSON schemas | 4 |
| Reused SQLite DDL tables | 12 |
| Candidate service operations | 34 |
| Candidate workflow models | 10 |
| Runtime obligations | 31 |
| Illustrative protocol messages | 79 |

The shared `common` schema defines reusable structures and has no standalone message example. New protocols are implementation messages, not newly admitted Artifact Types. Actual domain bodies continue to use their selected registered contracts.

## Read the design

1. [Architecture and Agent interaction](ARCHITECTURE.md).
2. [Every protocol schema, its purpose and example](SCHEMAS.md).
3. [All bound domain contract versions and their current/historical posture](DOMAIN-CONTRACTS.md).
4. [Ten workflow models and completion requirements](WORKFLOWS.md).
5. [Runtime obligations](RUNTIME-OBLIGATIONS.md).
6. [Contract fit and unresolved integration decisions](FIT-REPORT.md).
7. [Review and authoring evidence](REVIEW.md).

The [package manifest](package-manifest.json), [source baseline](SOURCE-BASELINE.json) and [authoring receipt](receipts/schema-authoring.json) bind exact files. Receipt generation does not authorize an effect.

## Storage choice represented here

Existing canonical files retain their current source/admission role. Future exact-byte packages and immutable commit records can capture selected new operational content. SQLite is a rebuildable query projection. File generation exports selected original bytes or renders a view with a pinned renderer. Lab and ontology retain explicit, separate source cuts and authorities.

The underlying candidates are [storage proposal 0006](../0006-lab-artifact-storage/PROPOSAL.md) and [the integrated roadmap](../../plans/0009-lab-integrated-roadmap/PLAN.md). This package adds no performance or storage-saving measurement.

## Admission boundary

A future complete review package can present independent exact Decision cores in one final owner checkpoint. All required owners must authorize their exact members. Deterministic canonical consequences and derived generations retain provenance to that authorization. Local action effects, repository admission and release acceptance keep their own scopes.

This package does not authorize unknown future Work, lessons, signatures, installations, external effects or service activation. Selected protocols forbid network scopes and external effects; admission transactions permit zero runtime activations. The owner review will occur after the exact implementation package and its required evidence exist.
