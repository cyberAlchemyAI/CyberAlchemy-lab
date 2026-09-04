<!-- GENERATED FILE: edit artifact.json and rerun generator.py. -->

# Bounded Context artifact type v1

> Generated from `artifact.json`; this view is not canonical.

- Artifact type: `cal.artifact-type.bounded-context/v1`
- Candidate version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Definition: `cal.definition.bounded-context`

## Representation contract

- Canonical machine file: `context.json`
- Generated human file: `CONTEXT.md`
- Stable identity field: `context_id`
- Schema: `cal.schema.bounded-context/v1`

## Distinct validation purpose

Proves explicit versioned semantic-boundary identity, model, language, owner, scope, and separately mapped cross-context dependencies.

## Orthogonality rules

| Rule | Mode | Requirement |
| --- | --- | --- |
| `CTX01-BC-01` | `deterministic` | Directory placement never supplies Bounded Context identity. |
| `CTX01-BC-02` | `deterministic` | A Bounded Context remains distinct from Coordination Context and Ubiquitous Language. |
| `CTX01-BC-03` | `hybrid` | Cross-context dependencies are represented only by explicit Context Map references. |

## Four facets

### Classification

The artifact type, semantic kind, authority kind, lifecycle posture, and context identity are explicit independent fields.

### Schema

The closed Bounded Context schema requires stable identity, exact version, model, language, scope, owner, and map references.

### Human Continuation

CONTEXT.md is generated from context.json and exposes boundaries, evidence, residue, and challenge route.

### Machine Checkable

Schema validation, hostile fixtures, exact dependency digests, semantic checks, and projection parity are collected by validate.py.

## Remaining residue

- `CTX01-BC-R1` — No artifact-type-owner admission decision binds this candidate. Consequence: No Bounded Context instance may rely on this candidate as an admitted type.
- `CTX01-BC-R2` — No operational bounded-context owner role is bound. Consequence: Governance and Ontology Lifecycle context instances remain blocked.

## Claim ceiling

This package is a Bounded Context/v1 artifact-type candidate. PASS proves only its exact schema, dependency, fixture, orthogonality, and projection checks; it does not admit the type or create a context.
