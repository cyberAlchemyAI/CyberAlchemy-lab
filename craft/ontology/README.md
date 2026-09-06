# DomainSpec Product Ontology

Status: canonical project-local ontology package

Ontology ID: `domainspec-product-ontology@1`

Ontology type: `business-system-bridge`

Owner: DomainSpec v2 owner
Visibility: private

## Purpose

This package explains DomainSpec as one evidence-bound product model. It connects the product thesis and
domain language to the implementation baseline, instantiation CLI, target observers, receipts, and current
residue without letting any read model replace its source authority.

The ontology is canonical for **product navigation and traceability**. It does not redefine terms, alter
DS-D1 or DS-D8, select implementation bytes, prove runtime behavior, or authorize publication, deployment,
or release.

## Package

| Artifact | Role |
| --- | --- |
| [`profile.json`](profile.json) | Stable package identity, type selection, ownership, branches, current baseline, and authority ceiling. |
| [`sources.json`](sources.json) | Exact source paths, roles, branches, and SHA-256 identities. |
| [`nodes.json`](nodes.json) | Stable business and system concepts. |
| [`relations.json`](relations.json) | Typed business/system and system-internal relations with explicit evidence. |
| [`residue.json`](residue.json) | Open product gaps that the ontology must not smooth into completion. |
| [`views/business.md`](views/business.md) | Human business/product view. |
| [`views/system.md`](views/system.md) | Human implementation view. |
| [`views/bridge.md`](views/bridge.md) | Human intent-to-implementation traceability view. |
| [`schema/ontology-package.schema.json`](schema/ontology-package.schema.json) | Closed record-shape contract used by the validator. |
| [`schema/2026-08-29-business-relations-and-residue-node-bindings.json`](schema/2026-08-29-business-relations-and-residue-node-bindings.json) | Schema-amendment witness for business relations and explicit residue node bindings. |
| [`schema/2026-08-30-designed-system-components.json`](schema/2026-08-30-designed-system-components.json) | Schema-amendment witness for explicit `designed` system nodes and designed realization topology. |
| [`schema/2026-08-30-infrastructure-binding-contracts.json`](schema/2026-08-30-infrastructure-binding-contracts.json) | Migration witness for concern-specific contracts and explicit infrastructure bindings. |
| [`schema/2026-08-30-repository-bridge-non-collapse.json`](schema/2026-08-30-repository-bridge-non-collapse.json) | Non-collapse witness routing business semantics through the Repository contract before an adapter. |
| [`validate-ontology.mjs`](validate-ontology.mjs) | Deterministic source-currentness, closure, polarity, evidence, and receipt validator. |
| [`validation-receipts/`](validation-receipts/) | Append-only package validation history. |

The machine JSON files are the ontology state. Markdown files are human views and must not contradict them.

## Product in one graph

```text
checked system map
  -> typed domain graph
  -> exact realization baseline
  -> deterministic instantiation CLI
  -> independent target observer
  -> baseline-bound receipt
  -> external owner decision

Workflow failure
  -> immutable Recovery Intent
  -> Durable Compensation Dispatch over a frozen plan
  -> fenced Claim with time-bounded Lease
  -> Execution Attempt with stable Invocation Identity
  -> completed | bounded Retry | exhausted | escalated
```

## Authority boundaries

- [`../PRODUCT-THESIS.md`](../PRODUCT-THESIS.md) owns product positioning.
- [`../definitions/DEFINITIONS.md`](../definitions/DEFINITIONS.md) owns critical term semantics.
- [`../definitions/meta-types/meta-types.md`](../definitions/meta-types/meta-types.md) owns DS-D1 human cards.
- [`../definitions/relationships/relationships.yml`](../definitions/relationships/relationships.yml) owns DS-D8 signatures.
- Baseline `domainspec-meta-types-current-implemented@10` owns the selected baseline-independent recovery closure and provider-neutral system-integration formation epoch; current state, Node 26, catalog, and receipt projections are exact-validated outside its digest membership.
- Runtime contracts own bounded operational behavior.
- This ontology owns only the stable cross-source graph and its explicit gaps.

## Compensation admission

The complete compensation model is admitted as `domainspec-v2-D36..D44`. D36 is the umbrella forward-recovery
model; D37 owns the Recovery Intent, D38 durable Dispatch, D39 execution Attempt, D40 replay-safe Invocation
Identity, D41 exclusive fenced Claim, D42 time-bounded Claim Lease, D43 bounded Retry, and D44 Terminal
Disposition. These are runtime method concepts around existing Workflow and Operation types, not new DS-D1
meta-types or DS-D2/DS-D8 verbs.

Candidate-local generated TypeScript, Python, and Rust implementations bridge D36 in-process
planning/execution, D37 deterministic Recovery Intent, and D40 stable plan-occurrence Invocation Identity to
the external-executor boundary. Their shared profile hash-closes each target, test, and Workflow binding. This
is selected into baseline v10 only as bounded generated-source and contract-profile formation. The remaining D38/D39/D41/D42/D43/D44 durable
machinery and Operation-owned persistent replay recognition remain bound to explicit residue.

The canonical target machinery is now a first-class system ontology. It contains concern-specific Repository,
Unit of Work, Clock, Wakeup, binding-resolution, and telemetry contracts plus separate persistence,
transaction-guarantee, failure-outcome, and durable-workflow-runtime bindings. These surround one logical
transactional Recovery Coordination Store, fenced Claim authority, Lease service, durable Worker, Attempt journal,
Operation-owned Invocation Ledger, Retry scheduler, Terminal recorder, Restart reconciler, dispatch-outbox
publisher, Clock contract, and telemetry contract. The D45-D49 contract and binding-formation nodes are now
`implemented`; provider adapters, durable workers, journals, schedulers, restart components, and telemetry
remain `designed`. The portable architecture-property profile remains canonical. See
[`../architecture/durable-recovery/README.md`](../architecture/durable-recovery/README.md).

## Integration research admission

The D45-D49 integration-boundary subgraph preserves the exact provenance used to design that machinery:
the Operation, Workflow, and Infrastructure-Binding Pattern Tower; System Integration Contract Layer
Revision 2; and the explicit owner admission. The Tower supplies the non-collapse model, Revision 2 supplies
the candidate ownership split and first portable binding records, and the owner admission makes the semantic
distinctions canonical.

The ontology keeps those roles separate. The two research records have `authority_effect: none`, while live
profile, compiler, validator, CLI, receipt, observer, and hostile-test sources now provide bounded formation
evidence for the implemented `impl/system-integration/` package. This does not retrofit implementation
authority into the research or admission. No universal Port, mandatory Interface, provider, database, ORM,
broker, durable runtime, or deployment is selected, and no provider runtime guarantee is observed.

## Validate

Run with the repository Node 26 environment:

```text
node validate-ontology.mjs --require-receipt
```

Validation checks exact source digests, closed keys, stable-ID uniqueness, relation endpoint closure, business,
system, and bridge polarity, separate business/system evidence on every bridge edge, view references, baseline
currentness, the three-language recovery profile and its claim ceiling, D36-D44 non-collapse,
the D45-D49 research-to-admission-to-system bridge, implementation-gap bindings, and the highest numeric
append-only receipt epoch.

## Evolution

Change source authority first. Then update the ontology records and their source digests, validate without
writing, append a new receipt, and validate again with `--require-receipt`. Never overwrite an earlier receipt
or infer that a source change preserves an earlier baseline or package digest.
