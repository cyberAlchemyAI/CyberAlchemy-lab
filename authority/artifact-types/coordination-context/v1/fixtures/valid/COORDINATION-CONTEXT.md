<!-- GENERATED FILE: edit coordination-context.json and rerun generator.py. -->

# Coordination Context: fixture.coordination.example

> Generated from `coordination-context.json`; this view is not canonical.

- Identity: `fixture.coordination.example`
- Version: `1.0.0-fixture`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.coordination-context/v1`
- Semantic kind: `coordination-context`
- Authority effect: `none`

## Product Ref

fixture.product.example/v1

## Project Ref

fixture.project.example/v1

## Goal Ref

`null`

## Purpose

Exercise durable work framing without semantic-boundary collapse.

## Consumer Refs

- fixture:consumer:agent

## Intended Uses

- fixture validation

## Subject Scope

```json
{
  "exclusions": [
    "No execution authority."
  ],
  "statement": "Fixture-only coordination scope."
}
```

## Source Policy Refs

- fixture:source-policy

## Bounded Context Refs

- fixture.context.example/v1

## Owner Ref

fixture:role:coordination-owner

## Revision History

None declared.

## Challenge Route

fixture:route:coordination-challenge

## Evidence

- fixture:evidence:coordination

## Residue

- fixture:residue:owner-unbound

## Claim ceiling

Fixture only; it does not create a Coordination Context or grant execution authority.
