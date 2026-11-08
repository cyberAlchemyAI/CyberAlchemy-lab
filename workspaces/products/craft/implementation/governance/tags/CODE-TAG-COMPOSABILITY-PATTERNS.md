# Code Tag Composability Patterns

This document defines implementation composition obligations derived from active
root DS-D8 relationship authority in
`projects/domainspec-v2/definitions/relationships/relationships.yml`. The checker consumes that
authority; this document is an implementation projection and does not own edge
labels or endpoint signatures.

## Purpose

Edges describe domain semantics. Composability patterns make those semantics executable by defining how related symbols must reference each other in code.

These patterns are aligned with the functional layering model in `ARCHITECTURE.md`:

- Domain rules/calculations/policies are pure and called by application operations.
- Interface and UI bindings call application use-cases through explicit boundaries.
- Workflows orchestrate operations in dependency order.

## Pattern Matrix

| Edge             | From -> To               | Required Composition                                 | Reference Concept                                         | Enforced by Tool |
| ---------------- | ------------------------ | ---------------------------------------------------- | --------------------------------------------------------- | ---------------- |
| `enforces`       | Rule -> Operation (same/cross feature) | Operation calls rule before mutation        | `billing.MaxAmountRule -> billing.ProcessPayment`         | Yes              |
| `enforces-cross` | deprecated alias         | Do not author; use `enforces` in the cross-feature spec surface | `compliance.AccessRule -> payments.ProcessRefund` | Rejected          |
| `calculates`     | Calculation -> Operation | Operation calls calculation and consumes result      | `billing.FeeCalculation -> billing.ProcessPayment`        | Yes              |
| `applies`        | Policy -> Operation/Calculation | Target calls policy to select strategy branch | `billing.RetryPolicy -> billing.ProcessPayment`           | Yes              |
| `exposes`        | Interface -> Operation   | Interface/controller calls operation use-case        | `billing.PaymentAPI -> billing.ProcessPayment`            | Yes              |
| `exposes`        | Interface -> Query       | Interface/controller calls query use-case            | `billing.PaymentAPI -> billing.GetPaymentStatus`          | Yes              |
| `orchestrates`   | Workflow -> Operation[]  | Workflow calls listed operations                     | `billing.SettlementWorkflow`                              | Yes              |
| `mutates`        | Binding -> Operation     | Binding hook/action calls operation                  | `ui.billing.useCreatePayment -> billing.ProcessPayment`   | Yes              |
| `fetches`        | Binding -> Query         | Binding hook/action calls query                      | `ui.billing.usePaymentStatus -> billing.GetPaymentStatus` | Yes              |
| `produces`       | Operation -> Event       | Operation emits/publishes event after postconditions | `billing.ProcessPayment -> billing.PaymentCompleted`      | Not yet          |
| `transitions`    | Event -> State Machine   | Transition map handles event input                   | `billing.PaymentCompleted -> billing.PaymentLifecycle`    | Not yet          |
| `contracts`      | Form -> Interface        | Form submit path calls matching interface contract   | `ui.billing.CreatePaymentForm -> billing.PaymentAPI`      | Not yet          |
| `consumes`       | Component -> Hook        | Component references and invokes hook                | `ui.billing.PaymentPanel -> ui.billing.usePaymentStatus`  | Not yet          |

## Pattern 1: Rule Enforces Operation

Semantic contract:

- `Rule --enforces--> Operation`
- Operation invokes rule before mutation path.

Reference snippet:

- `governance/tags/examples/composability/rule-enforces-operation.ts`

## Pattern 2: Deprecated Cross-Feature Alias

Semantic contract:

- `enforces-cross` is not canonical authored DS-D8 authority.
- Author `Rule --enforces--> Operation`; declare cross-feature placement in the
  specification's Cross-Feature Dependencies surface.
- Strict checking rejects the alias with replacement guidance.
- The code-tag checker validates the active verb, endpoints, and call obligation;
  it does not infer feature placement from code symbols alone.

Reference snippet:

- `governance/tags/examples/composability/enforces-cross-operation.ts`

## Pattern 3: Calculation Calculates Operation

Semantic contract:

- `Calculation --calculates--> Operation`
- Operation invokes calculation and uses output in state/mutation decision.

Reference snippet:

- `governance/tags/examples/composability/calculation-calculates-operation.ts`

## Pattern 4: Policy Applies Operation

Semantic contract:

- `Policy --applies--> Operation`
- Operation delegates strategy selection to policy.

Reference snippet:

- `governance/tags/examples/composability/policy-applies-operation.ts`

## Pattern 5: Interface Exposes Operation

Semantic contract:

- `Interface --exposes--> Operation`
- Interface/controller invokes operation use-case directly.

Reference snippet:

- `governance/tags/examples/composability/interface-exposes-operation.ts`

## Pattern 6: Interface Exposes Query

Semantic contract:

- `Interface --exposes--> Query`
- Interface/controller invokes query use-case directly.

Reference snippet:

- `governance/tags/examples/composability/interface-exposes-query.ts`

## Pattern 7: Workflow Orchestrates Operations

Semantic contract:

- `Workflow --orchestrates--> Operation[]`
- Workflow coordinates declared operations in sequence/branch/compensation logic.

Reference snippet:

- `governance/tags/examples/composability/workflow-orchestrates-operations.ts`

## Pattern 8: Binding Mutates Operation

Semantic contract:

- `Binding --mutates--> Operation`
- UI binding/hook calls operation on mutation path.

Reference snippet:

- `governance/tags/examples/composability/binding-mutates-operation.ts`

## Pattern 9: Binding Fetches Query

Semantic contract:

- `Binding --fetches--> Query`
- UI binding/hook calls query on read path.

Reference snippet:

- `governance/tags/examples/composability/binding-fetches-query.ts`

## Tooling Rule Source

Endpoint rules are loaded from:

- `projects/domainspec-v2/definitions/relationships/relationships.yml` — root DS-D8 authority.

Code-call semantics are implemented in:

- `governance/tags/tools/check-code-tag-composability.ts`

Current blocking/validation codes:

- `CT-COMP-001`..`CT-COMP-008` for supported call-composition mismatches
- `CT-COMP-010` target concept not tagged
- `CT-COMP-011` source symbol unresolved
- `CT-COMP-012` target symbol unresolved
- `CT-COMP-013` root relationship authority unavailable or invalid
- `CT-COMP-020` generated view authored as a canonical edge
- `CT-COMP-021` deprecated relationship alias authored
- `CT-COMP-022` deferred relationship candidate authored as active
- `CT-COMP-023` active label used with invalid endpoint types
- `CT-COMP-024` valid active signature lacks code-call semantics (coverage gap)
- `CT-COMP-025` unknown relationship label

The JSON report names the authority path, active signature count, generated /
deprecated / deferred counts, derived call-rule count, and every unsupported
active call-semantic signature. Current root state is 31 active signatures and
nine derived call-semantic rules.

## Aggregate Gate Status

`tags:composability` remains an explicit command rather than part of `npm run
validate`. The default extraction input `governance/tags/code-tags.json` is not
currently committed, so unconditional aggregate wiring would fail on missing
setup state rather than a verified code-graph violation. A later extraction/CI
task must provide a stable input before aggregate promotion.
