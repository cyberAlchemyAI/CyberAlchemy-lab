<!-- GENERATED FILE: edit coordination-context.json and rerun generator.py. -->

# Coordination Context: cal.coordination-context.ontology-product

> Generated from `coordination-context.json`; this view is not canonical.

- Identity: `cal.coordination-context.ontology-product`
- Version: `1.0.0-test-candidate.1`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.coordination-context/v1`
- Semantic kind: `coordination-context`
- Authority effect: `none`

## Product Ref

CA2-PRODUCT-ONTOLOGY/v1

## Project Ref

`null`

## Goal Ref

`null`

## Purpose

Coordinate Product-level ontology package evolution across Governance and Ontology Lifecycle while keeping source meaning, Product identity, context ownership, and runtime implementation distinct.

## Consumer Refs

- role:ontology-product-owner
- role:governance-context-owner
- role:ontology-lifecycle-context-owner
- role:ontology-product-runtime-binding-owner

## Intended Uses

- bind one governed ontology-package contract to replaceable lifecycle runtime implementations
- test deterministic evolution, replay, recovery, and runtime replacement
- surface context or runtime drift without transferring semantic authority

## Subject Scope

```json
{
  "exclusions": [
    "The Coordination Context does not own Governance or Ontology Lifecycle meaning.",
    "The Coordination Context does not make a runtime, projection, checkpoint, or Product package canonical source meaning.",
    "The Coordination Context does not admit contexts or runtimes, approve the Product, or authorize activation, cutover, publication, release, deployment, or source retirement."
  ],
  "statement": "The coordination boundary covers the Ontology Product package contract, its Governance and Ontology Lifecycle semantic dependencies, and replaceable runtime bindings used only to calculate Product observations."
}
```

## Source Policy Refs

- docs/migration-plans/0005-ontology-product-context-runtime-bindings-v1/plan.json
- contexts/maps/governance-ontology-lifecycle/v2/map.json
- product/products/ontology/v1/contracts/ontology-package.schema.json

## Bounded Context Refs

- cal.context.governance/v2
- cal.context.ontology-lifecycle/v2

## Owner Ref

role:ontology-product-owner

## Revision History

```json
[
  {
    "decision_ref": "user-direction:implement-L3-context-runtime-bindings-and-evolution-recovery-tests",
    "revision": "1.0.0-test-candidate.1"
  }
]
```

## Challenge Route

role:ontology-product-owner

## Evidence

- product/products/ontology/v1/candidates/0002-source-preserving-foundation/receipts/validation.json
- contexts/governance/v3/context.json
- contexts/ontology-lifecycle/v3/context.json
- contexts/maps/governance-ontology-lifecycle/v2/map.json
- implementation/bindings/ontology-product-lifecycle/v1/binding.json

## Residue

- residue:coordination-context-artifact-type-remains-unadmitted
- residue:ontology-product-coordination-owner-admission-not-performed
- residue:runtime-binding-remains-replaceable-test-candidate

## Claim ceiling

This candidate coordinates Product tests over exact context references and replaceable runtime bindings. It does not become a semantic Bounded Context, own source meaning, admit a context or runtime, approve the Product, or authorize operational effects.
