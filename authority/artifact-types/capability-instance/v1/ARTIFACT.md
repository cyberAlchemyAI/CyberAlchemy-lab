<!-- GENERATED FILE: edit artifact.json and rerun generator.py. -->

# Capability Instance artifact type v1

> Generated from `artifact.json`; this view is not canonical.

- Artifact type: `cal.artifact-type.capability-instance/v1`
- Candidate version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Definition: `cal.definition.capability-instance`

## Representation contract

- Canonical machine file: `instance.json`
- Generated human file: `INSTANCE.md`
- Stable identity field: `capability_instance_id`
- Schema: `cal.schema.capability-instance/v1`

## Distinct validation purpose

Proves an owner-local realization of one exact Product Capability while preserving parent/instance authority, contract, construction, conformance, recursion, and handoff separation.

## Orthogonality rules

| Rule | Mode | Requirement |
| --- | --- | --- |
| `CTX01-CI-01` | `deterministic` | Capability Instance identity and authority remain distinct from its parent Product Capability. |
| `CTX01-CI-02` | `deterministic` | Context membership is explicit and never inferred from directory placement. |
| `CTX01-CI-03` | `hybrid` | Conformance evidence never grants authority and recursion always has a stop and recomposition route. |

## Four facets

### Classification

Parent model, local instance, authority claims, contexts, lifecycle, and conformance remain independent.

### Schema

The closed schema requires the exact parent, local contexts, separate claims, inherited contract, construction binding, recursion stop, recomposition, and handoff.

### Human Continuation

INSTANCE.md is generated and exposes the complete recursive continuation and residue surface.

### Machine Checkable

Schema, identity and authority separation, recursion, dependency, fixture, and projection checks are executable.

## Remaining residue

- `CTX01-CI-R1` — No artifact-type-owner admission decision binds this candidate. Consequence: No Capability Instance may rely on this candidate as an admitted type.
- `CTX01-CI-R2` — No exact parent Product Capability and operational instance owner are selected for the migration target. Consequence: No real capability instance can be authored.

## Claim ceiling

This package is a Capability Instance/v1 artifact-type candidate. PASS does not instantiate, adopt, bind, conform, or grant authority to a Product Capability.
