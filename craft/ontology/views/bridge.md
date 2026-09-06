# DomainSpec Product Ontology — Business/System Bridge

Every bridge relation below cites separate business and system sources in `relations.json`.

```text
dsv2.product.checked-system-map
  --realized_by--> dsv2.system.instantiation-cli
  --tested_by----> dsv2.system.contract-tests

dsv2.product.typed-domain-graph
  --realized_by--> dsv2.system.instantiation-cli

dsv2.product.exact-realization
  --realized_by--> dsv2.system.baseline-v10

dsv2.product.non-inflating-evidence
  --realized_by--> dsv2.system.target-observer

dsv2.product.workflow-compensation
  --realized_by--> dsv2.system.compensation-planner [TypeScript, Python, Rust candidate evidence]
  --realized_by--> dsv2.system.compensation-executor [TypeScript, Python, Rust in-process evidence]
  --realized_by--> dsv2.system.durable-recovery-worker [designed]
  --tested_by----> dsv2.system.contract-tests

dsv2.compensation.intent
  --realized_by--> dsv2.system.compensation-planner
  --realized_by--> dsv2.system.recovery-coordination-repository-contract [designed]

dsv2.compensation.invocation-identity
  --realized_by--> dsv2.system.compensation-planner
  --realized_by--> dsv2.system.operation-invocation-ledger [designed]

dsv2.compensation.dispatch
  --realized_by--> dsv2.system.recovery-coordination-repository-contract [designed]

dsv2.compensation.attempt
  --realized_by--> dsv2.system.recovery-attempt-journal [designed]

dsv2.compensation.claim
  --realized_by--> dsv2.system.recovery-claim-authority [designed]

dsv2.compensation.claim-lease
  --realized_by--> dsv2.system.recovery-lease-service [designed]

dsv2.compensation.retry
  --realized_by--> dsv2.system.recovery-retry-scheduler [designed]

dsv2.compensation.terminal-disposition
  --realized_by--> dsv2.system.recovery-terminal-recorder [designed]

dsv2.integration.dependency-contract
  --realized_by--> dsv2.system.recovery-architecture-profile

dsv2.integration.persistence-binding
  --realized_by--> dsv2.system.recovery-persistence-binding [designed]

dsv2.integration.transaction-guarantee-binding
  --realized_by--> dsv2.system.recovery-transaction-guarantee-binding [designed]

dsv2.integration.failure-outcome-binding
  --realized_by--> dsv2.system.recovery-failure-outcome-binding [designed]

dsv2.integration.durable-workflow-runtime-binding
  --realized_by--> dsv2.system.durable-workflow-runtime-binding [designed]
```

Reverse traceability keeps system evidence subordinate to meaning:

```text
dsv2.system.target-observer
  --traced_to--> dsv2.language.meta-types
  --traced_to--> dsv2.language.relationships
```

The bridge asserts alignment only for the exact cited source identities. The three-language recovery profile
is selected by baseline v10 only as bounded generated-source and contract-profile formation. A changed source digest makes the
package stale and requires a new validation receipt.

The `[designed]` bridges assert canonical target topology, not implementation alignment. Their system nodes
and the semantic nodes remain explicitly bound to `dsv2.residue.durable-compensation-dispatch` until durable
runtime evidence exists. D38/D39/D41/D42/D43/D44, provider persistence, restart recovery, and Operation-owned
durable replay recognition remain open.

The integration bridges cite canonical D45-D49 and the owner admission on the business side, and the exact
Tower, Revision 2, durable-recovery architecture, provider-neutral profile/compiler/tests, CLI compiler/tests,
receipt schema, and target observer on the system side. This proves formation and static-observation alignment;
provider realizations, durable runtime behavior, and runtime-guarantee evidence remain absent.
