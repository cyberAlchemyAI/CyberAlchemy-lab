<!-- GENERATED FILE: edit artifact.json and rerun generator.py. -->

# Coordination Context artifact type v1

> Generated from `artifact.json`; this view is not canonical.

- Artifact type: `cal.artifact-type.coordination-context/v1`
- Candidate version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Definition: `cal.definition.coordination-context`

## Representation contract

- Canonical machine file: `coordination-context.json`
- Generated human file: `COORDINATION-CONTEXT.md`
- Stable identity field: `coordination_context_id`
- Schema: `cal.schema.coordination-context/v1`

## Distinct validation purpose

Proves durable work framing with one Product, optional Project and Goal, explicit consumers and uses, and references to independently owned semantic contexts.

## Orthogonality rules

| Rule | Mode | Requirement |
| --- | --- | --- |
| `CTX01-CC-01` | `deterministic` | Coordination Context is not a Bounded Context and cannot own its model or language fields. |
| `CTX01-CC-02` | `deterministic` | Exactly one Product and at most one Project and Goal are represented as separate references. |
| `CTX01-CC-03` | `hybrid` | A material anchor change requires successor review rather than silent identity mutation. |

## Four facets

### Classification

Coordination identity is explicit and separate from semantic context, Product, Project, Goal, authority, and lifecycle axes.

### Schema

The closed schema enforces product cardinality and explicit optional project and goal references without bounded-context fields.

### Human Continuation

COORDINATION-CONTEXT.md is generated from its machine record and preserves purpose, uses, evidence, residue, and challenge route.

### Machine Checkable

Schema, cardinality, non-collapse, dependency, fixture, and projection checks are deterministic except successor significance review.

## Remaining residue

- `CTX01-CC-R1` — No artifact-type-owner admission decision binds this candidate. Consequence: No Coordination Context instance may rely on this candidate as an admitted type.
- `CTX01-CC-R2` — No operational coordination-context owner role is bound. Consequence: Durable coordination instances remain blocked.

## Claim ceiling

This package is a Coordination Context/v1 artifact-type candidate. PASS does not admit the type, create a coordination record, or authorize work.
