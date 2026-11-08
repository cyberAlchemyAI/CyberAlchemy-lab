# Craft import: retain the structure, select current evidence

The reviewed import has been applied locally; see [implementation results](IMPLEMENTATION.md) and [APPLIED.json](APPLIED.json). The original staged allowlists remain the preparation inputs; later local bindings and Work/status changes are recorded in [LOCAL-CHANGES.json](LOCAL-CHANGES.json).

This proposal retains the detailed recursive Lab/Craft organization and its functional files. It does not minimize the folder structure, consolidate the concepts into seven files, or remove useful records because they are JSON. Selection depends on a file's purpose.

## Selection rule

**Keep:** current definitions, identities, capabilities, contracts, schemas, governing rules, applicable decisions/bindings, Goal definitions, plans, task/dependency records, current operational state, authored ontology models, source/configuration manifests, implementation inputs and necessary readable documentation.

**Exclude by default:** observed test/evaluation results, validation receipts, proof/assessment packets, source snapshots retained as evidence, captured sessions, saved execution runs/logs, old generated proof graphs and historical result archives. SFOL remains excluded.

**Selected current evidence:** the 2026-11-05 review adds a separate, explicit [current-evidence export](EVIDENCE-REVIEW.md): two exact November 3 proof files and one scope index under `craft/work/outcomes/current-verification/`. [EVIDENCE-EXPORT.json](EVIDENCE-EXPORT.json) is its three-file allowlist. It does not restore a historical evidence archive or change the functional payload allowlist below. Current source-digest applicability is checked separately from relocated-runtime qualification.

A Product record, Goal record, applicable authority binding or model source registry can be functional and stays. A test-result or attestation report used only to demonstrate a past run does not. A field such as evidence_requirements defines acceptance and is retained; the recorded evidence proving that acceptance is not imported. Likewise, a functional source binding can reference an input without copying that input's historical proof packet.

## Structure

```text
craft/
├── README.md
├── product/
│   ├── README.md / PRODUCT.md / product.json
│   ├── PRODUCT-THESIS.md / product-thesis.record.json
│   ├── relationships.json / scopes.json / roadmap.json
│   ├── capabilities/
│   │   ├── README.md / catalog.json
│   │   └── <14 families>/README.md + capability/contract/policy files
│   └── features/system-construction/
├── project/
│   ├── README.md / PROJECT.md / project.json
│   ├── OWNERS.md / owners.json
│   ├── GOALS.md / goals.json
│   ├── DEPENDENCIES.md / dependencies.json
│   ├── coordination.json / work-index.json
│   └── CURRENT-STATE.md / current-state.json / WORK.md
├── work/
│   ├── README.md / CURRENT.json / work.json
│   ├── goals/ / plans/ / tasks/ / ledger/
│   ├── blockers/ / outcomes/
│   └── initiatives/ / processes/ / research/ / discovery/ / experiments/
├── authority/
│   ├── README.md / authority.json / AUTHORITY-MODEL.md
│   ├── definitions/ / owners/ / constitutions/ / axioms/ / policies/
│   ├── decisions/ / method-bindings/ / lineage/ / shared/
│   └── attestations/ / imports/ / residue/
├── ontology/
│   ├── README.md / ONTOLOGY.md / ontology.json
│   ├── identity-graph.json / catalog.json
│   ├── application/ / views/inputs/
│   ├── packages/product-bridge/ / packages/orodi-bridge/
│   ├── business/ / system/ / bridges/ / profiles/ / schemas/ / sources/
│   └── shared/ / external/ / residue/ / derived/
├── architecture/
├── implementation/
│   ├── cli/ / alchlang/ / profiles/ai/
│   ├── test-derivation-engine/ / formalization/
│   └── runtime/ / lab-integration/
└── docs/guide/ + docs/reference/
```

[Craft README](proposed/craft/README.md) links the eight concept/implementation/documentation homes. Each child has its own readable route. There is no copied craft/evidence tree or archive of the removed records. The derived directory contains instructions only, not generated results.

## Functional contents

| Area | Kept in the proposal | Evidence-only files excluded |
|---|---|---|
| Product | Identity/v2 candidate, thesis, Feature definition, 37 capabilities in 14 families, contracts, policies, scope and current roadmap. Generation, profiles, TDE and EVF stay. | Capability audit snapshots, test archives, saved source mirrors and old comparison packets. |
| Project | Existing Project identity, owners, two current Goal definitions, coordination, dependencies and current work/state. | Historical execution/closeout evidence and source-copy packets. |
| Work | Current selected work, Goal acceptance requirements, actionable plan, tasks/dependencies, current ledger entry and blockers. | Old task-occurrence inventories, ledger history, saved experiments, outcome assessments and captured research results. |
| Authority | Current definitions and normative schemas, governing rules, owner routes, applicable decision references, Method binding, identity lineage and shared contracts. | Review findings, attestation/test reports, validation receipts and mirrored authority evidence. |
| Ontology | Authored native Product and ORODI model records, schemas, functional source bindings, admitted identity base, input/output definitions and application configuration. | Graphs exported only as past proof, runtime/event-history snapshots, receipt registries and SFOL packages. |
| Architecture/docs | Current architecture, dependency rules, usage and concept explanations. | Historical presentations or saved rendered proof outputs. |
| Implementation | The detailed component locations and binding/configuration records remain. Current Craft-owned source, tests, fixtures, schemas, templates and build inputs are staged under their component homes; shared runtime installations remain referenced. Required source, tests, schemas and build configuration are functional inputs; they are not removed merely to reduce a file count. | Saved build/test outputs, dependency mirrors imported as evidence, proof archives and old run directories. |

The ORODI Goal is a prepared Goal/v1 candidate with acceptance definitions; achieved-condition assessments are not copied. Existing source admission and current candidate proposals remain distinct. The Project reverse membership for this Goal is not silently admitted.

## Ontology Lifecycle application

The application input manifest uses the existing v4 source-consumer contract. It maps the identity base, Product bridge and ORODI bridge: **84 native nodes and 117 relations** including identity records. Source model schemas and package identifiers are retained; no universal normalized source graph is invented.

Nine input-view definitions select Product, Project, Work, Authority, identity, business, system, traceability and verification requirements. The evidence-named view reads acceptance requirements and declared status; it imports no observed test/proof records. The application derives named consumer outputs on demand.

The native source consumer and named reading adapter are implemented and locally tested. The approved current-claim review is applied: 74 selected functional sources match, namespace errors are corrected, and historical result/projection dependencies are removed. Product adoption and effective runtime authority are not inferred. A structurally correct manifest does not make stale source bindings current. Old receipt PASS is neither imported nor reused. Original source expectations are not silently refreshed; only the new input manifest binds the prepared functional files.

## Restored functional material

All 37 capability records again carry participant/consumer references, input/output contracts, context policies, owner routes, scope, lifecycle posture and realization links. All 37 capability carriers validate against the existing Lab Product Capability/v1 schema; all 37 realization bindings validate against Realization Binding/v2. Empty required evidence/history fields preserve the native contract without importing proof records.

Six ORODI functional binding sets come from current upstream source interfaces. The other 31 local proposal binding sets were reconstructed from the retained capability meaning, current contracts and component locations. Their origins are explicit in each family's source-bindings.json. They remain candidates; neither reconstruction nor schema validation is adoption or runtime conformance.

Current implementation inputs are restored for Core, AlchLang, its extensions, AI profiles, TDE, system integration, operational resilience, architecture conformance, governance/source tools, specification, formalization and the EVF Rust workspace. This includes current test code, frozen/synthetic fixtures, executable templates, grammar files, build locks/configuration and the bundled native bridge required by the package. These are functional source inputs, not a mirror of saved proof runs.

The source packages still contain required legacy-named logic/compatibility dependencies, including modules used by TDE. Keep those dependencies so existing APIs/typechecks do not break. The standalone SFOL framework/Product capability and its old closure/evidence packets are not reintroduced. A fixture or schema named receipt/evidence is also retained when it is an input to current tests; an observed receipt/result file is excluded.

Selected current plan graphs and protocols are restored, with 114 source-qualified task definitions across three source plans. The current research definitions, experiment protocol, discovery scope and relocation process are present; completed-run reports/progress audits are not imported. Source-declared task status is not a fresh runtime assessment.

Shared Node/Cargo/dependency installations and shared ARE/ontology runtime code are not duplicated. The explicit source-layout and build-input bindings map the current source roots and 14 TypeScript extends bindings. The legacy Lab craft/tsconfig.base.json remains untouched; the new source base configuration is staged under craft/implementation/config/.

Native consumer preflight is a read-only check. It does not import events, start a service, qualify the named semantic view adapter or discharge current source-pin/owner/native/host checks. These remaining integration tasks were not deleted files to restore and are not claimed completed here.

## Review and execution

[IMPORT.json](IMPORT.json) lists every selected prepared functional file with its role, destination and current digest. [EVIDENCE-EXPORT.json](EVIDENCE-EXPORT.json) separately lists the three selected current Work outcome files. PLAN.md, the allowlists, APPLY.json, EVIDENCE-REVIEW.md, validate.py and VALIDATION.json are review tools and are not payload files.

Validation checks the restored structure and reader links, role-based exclusions, Product/Project/Goal/identity schema contracts, 37 capability descriptions, native ontology schemas and endpoint closure, source-file preservation/rebinding, component references, and application manifest/document pins. Source readiness and runtime/consumer qualification are reported separately; no historical result can satisfy a fresh acceptance check.

The local implementation has applied the Craft allowlists and selected evidence, configured dependency links and qualified the selected generated journey/readers. Shared installations, upstream source, existing stores and global consumer bindings remain unchanged.

The original `validate.py` checks preparation and pre-apply collision conditions; those conditions intentionally no longer hold after import. Use `node craft/implementation/run.mjs check` from the Lab root for the implemented local behavior, and `python3 -B docs/migration-plans/0007-craft-current-import-20261104/validate-live.py` for final import integrity.

[APPLY.json](APPLY.json) gives explicit current-digest guards and replacement/rebinding treatment for the three existing targets. Existing runtime entry points, stores, native graph bindings and unrelated active files are protected. The guarded apply completed; [APPLIED.json](APPLIED.json) records it. No blind overwrite, shared consumer switch or publication ran.

## Current verification

The applied import passes live schema/reference/navigation validation and 10 local tests. The current native manifest contains 3 packages, 84 nodes, 117 relations and 313 supporting documents. All 74 selected semantic sources match their current local/shared bytes. Body War is a source-present reference application; no historical results or saved generated projections were restored. See [the current source review](ONTOLOGY-UPDATE.md) and [local qualification](../../../craft/work/outcomes/current-verification/lab-qualification.json).
