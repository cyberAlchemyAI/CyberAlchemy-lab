# Code Tag Schema

This document defines the canonical source annotation contract for DomainSpec code tags.

## Purpose

Code tags connect implementation symbols to DomainSpec concepts and relationship edges in a machine-readable way.

## Canonical Shape

```yaml
domainspec:
  concept:
    id: payment.MaxAmountRule
    type: Rule
    concern: biz
    spec_ref:
      path: docs/features/payments/SPEC.md
      line: 7
      section: Concept Registry
  edges:
    - edge: enforces
      to: payment.ProcessPayment
      evidence: "Rule evaluated before operation execution"
```

## Field Contract

### Required

- `domainspec.concept.id`
- `domainspec.concept.type`

### Optional

- `domainspec.concept.concern` (`biz` or `sys`)
- `domainspec.concept.spec_ref.path` (relative SPEC path)
- `domainspec.concept.spec_ref.line` (row line in SPEC concept table)
- `domainspec.concept.spec_ref.section` (for example `Concept Registry`)
- `domainspec.edges` (array)
- `domainspec.edges[].edge`
- `domainspec.edges[].to`
- `domainspec.edges[].evidence`

## Semantics

- Edge direction is canonical and outbound from the tagged concept.
- Inverse aliases are not allowed.
- `concept.type` must match `meta_type` labels from `spec/meta-types/**/*.schema.yml`.
- `edges[].edge` must be canonical labels from the root relationship authority (`definitions/relationships/relationships.yml`).
- When present, `concept.spec_ref` must point to the same SPEC source row resolved from `concept.id`.

## Positive Example

```yaml
domainspec:
  concept:
    id: payment.PaymentAPI
    type: Interface
    concern: sys
  edges:
    - edge: exposes
      to: payment.ProcessPayment
```

Expected: valid.

## Negative Example (Missing Required)

```yaml
domainspec:
  concept:
    type: Rule
  edges:
    - edge: enforces
      to: payment.ProcessPayment
```

Expected: invalid (`domainspec.concept.id` missing).

## Negative Example (Invalid Concern)

```yaml
domainspec:
  concept:
    id: payment.MaxAmountRule
    type: Rule
    concern: business
```

Expected: invalid (`concern` must be `biz` or `sys`).

## Negative Example (Invalid Edge Direction Intent)

```yaml
domainspec:
  concept:
    id: payment.ProcessPayment
    type: Operation
  edges:
    - edge: enforces
      to: payment.MaxAmountRule
```

Expected: invalid (`enforces` must be `Rule -> Operation`).
