# Decision 0075: Lab Operational Runtime/v1 admission

Status: **owner admitted and applied**, 2026-10-07.

The owner explicitly admitted the exact reviewed Lab Operational Runtime/v1 implementation for local repository inspection, explicitly authorized local transactions, verified replay/recovery and ephemeral Agent context. One Decision core and one owner response authorized the admission and its deterministic repository consequences.

## Exact target and evidence

- [Target manifest](target.json): 24 reviewed package files and their digests, the exact validation receipt and the schema-valid Implementation representation.
- Reviewed package manifest digest: `ed552d46f18becd3e8f6206e0b069e190ff0c489530c70c2ae434a5938748864`.
- [Owner authorization](authorization.json): preserves the complete user instruction and exact target/core/evidence bindings. It records conversation authorization; it is not a fabricated cryptographic signature.
- [Immutable admission bundle](../../../authority/admissions/lab-operational-runtime/v1/bundle.json): preserves exact package/evidence copies and all admission records.
- [Application receipt](receipts/application.json): 17 schema-valid generated records, exact output hashes, unchanged reviewed files and both history cursors at 5.

## Effects

One implementation is admitted. A successor Project State at Decision 0075, one semantic event, one governance event, governance records, six declared deterministic Typed Relations and the output index are materialized in the same admission. The entire immutable bundle is published by one directory rename; Decision mirrors and the [current-state lookup](../../../authority/project-state-transitions/current.json) are generated projections of it.

The D74 state and histories remain byte-exact historical inputs. No canonical Definition, Artifact Type or Relation Kind is changed. The six runtime interface schemas remain implementation material.

## Source and execution boundary

Repository admission is now D75. The admitted runtime's unchanged source profile remains **D74**. Its verification receipt establishes that exact build and baseline, with 33 passing tests and a disposable operational demo. It does not establish execution against a new D75 profile. A future profile revision must explicitly integrate D75; no silent rebase occurs. Previously frozen stores detect the new repository epoch as stale.

The Implementation carrier's artifact revision is `@decision-0075`; the package revision is `v1`. The `implementation_version_ref` in the implementation overlay identifies the package version, not an alias for a Typed Relation endpoint. Its capability references describe the admitted bounded realization scope. No separate Capability Realization Binding adoption or global `realizes` connection is created.

No operational key or permanent store is provisioned. Runtime activations and external effects are **0**. Publication, deployment, multi-host operation, general organizational permissions, complete ontology coverage and power-loss durability remain outside this decision.

## Verification

```bash
python3 docs/decisions/0075-lab-operational-runtime-v1-admission/apply.py --check
```

The checker verifies the package/evidence, immutable bundle, exact owner/core/target links, schemas and relation endpoints, history chains, output hashes, D74 preservation and current-state lookup. It performs no new admission.
