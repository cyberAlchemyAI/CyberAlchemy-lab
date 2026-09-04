<!-- GENERATED FILE: edit artifact.json and rerun generator.py. -->

# Bounded Context artifact type v2

> Generated from `artifact.json`; this view is not canonical.

- Artifact type: `cal.artifact-type.bounded-context/v2`
- Candidate version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Definition: `cal.definition.bounded-context@2.0.0-candidate.1`
- Predecessor type: `cal.artifact-type.bounded-context/v1`

## Representation contract

- Canonical machine file: `context.json`
- Generated human file: `CONTEXT.md`
- Stable identity field: `context_id`
- Schema: `cal.schema.bounded-context/v2`

## Distinct validation purpose

Proves explicit versioned semantic-boundary identity, model, language, owner, scope, and contracts while rejecting canonical Context Map backreferences.

## Orthogonality rules

| Rule | Mode | Requirement |
| --- | --- | --- |
| `CTX07-BC-01` | `deterministic` | Directory placement never supplies Bounded Context identity. |
| `CTX07-BC-02` | `deterministic` | A Bounded Context remains distinct from its Ubiquitous Language and domain model. |
| `CTX07-BC-03` | `deterministic` | Context Map membership is forbidden as a canonical field on a Bounded Context. |
| `CTX07-BC-04` | `hybrid` | Reverse Context Map membership is a generated projection derived only from canonical maps. |

## Four facets

### Classification

Artifact type, semantic kind, authority kind, lifecycle posture, and context identity remain explicit independent fields; map membership is not another context axis.

### Schema

The closed v2 schema requires stable identity, exact version, model, language, scope, owner, contracts, and challenge route while rejecting context_map_refs and equivalent backreferences.

### Human Continuation

CONTEXT.md is deterministically generated from context.json and exposes scope, contracts, evidence, residue, and challenge route without adding map membership.

### Machine Checkable

Schema closure, admitted Definition currentness, predecessor preservation, hostile backreference rejection, semantic checks, and projection parity are executable.

## Remaining residue

- `CTX07-BC-R1` — No artifact-type-owner admission decision binds this v2 candidate. Consequence: No Bounded Context instance may rely on v2 as an admitted type.
- `CTX07-BC-R2` — Normalized Governance and Ontology Lifecycle successor contexts are not authored. Consequence: CTX05 context bytes remain the current admitted historical endpoints.

## Claim ceiling

This package is a Bounded Context/v2 artifact-type candidate. PASS proves only its exact schema, dependency, predecessor, hostile-fixture, normalization, and projection checks; it does not admit the type, create or revise a context, authorize migration, or establish a stable release.
