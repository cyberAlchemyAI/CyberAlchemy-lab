# Remaining migration work

Planning snapshot: 2026-09-08, after execution 0071. This list does not start builds or change the source checkout. Order is proposed, not a new approval requirement.

Source changes -> select a new snapshot -> compare with the imported snapshot -> validate affected evidence -> import an explicit successor.

The capability-description inventory has 41 imported candidates. That does not mean every capability's model, implementation and operational evidence has been migrated. Three examples remain examples, one experiment is excluded, and the card runtime remains deferred.

## Essays — resume after the current edits

| Order | Item and meaning | What needs to be done | Finished result |
| --- | --- | --- | --- |
| E1 | Refresh the source snapshot — identify the version we are importing | Compare your finished changes with 0071; record changed files, contracts, obligations and model references. Reuse unchanged evidence and rerun affected checks. | A new pinned snapshot and explicit change list; old receipts still refer to their original bytes. |
| E2 | Desktop build — turn source into a buildable app | Resolve pkg-config and native DBus/GTK/WebKit prerequisites as required by the actual build; rerun the locked desktop check. The last attempt timed out after missing pkg-config diagnostics. | A captured build result, with any remaining packaging gap named. |
| E3 | Platform adapter binding — connect platform-specific code to its evidence | Validate the nested Windows adapter binding, its dependency hashes, Linux-local evidence and platform selection. Repair stale references after E1. | Exact adapter binding; Linux checks and native Windows evidence remain distinct. |
| E4 | Client parity — the same command has the same meaning across clients | Build shared command/response traces for CLI, IPC, HTTP/SSE and desktop. The bridge currently has no linked parity test. | Comparable traces and explicit unsupported clients, rather than a blanket parity claim. |
| E5 | Recovery and transport — correct behavior during interruptions | Exercise crash points, replay, reconnect/cursors, peer credentials and negative authentication cases against temporary local state. Extend beyond the existing reopen/replay/DPoP unit cases. | Evidence for each claimed failure boundary. |
| E6 | Refresh coverage and implementation binding — point every claim at current evidence | Regenerate exact fingerprints and update affected mappings after E1–E5; preserve partial results where the campaign does not prove the obligation. | Current, reproducible bindings and an honest remaining-gap list. |
| E7 | Product and writing models — define Essays and its writing workflow | Fully validate/import `essays/ontology/product` and `essays/capabilities/writing/ontology`. Their predecessor material hashes were checked in 0068; full package imports remain separate. | Validated Product and writing contexts with explicit dependencies. |
| E8 | Broader Essays system model — check for another runtime scope | Audit `essays/system-ontology/PROFILE.json` and its DomainSpec project. It references writing/product-inspection capabilities distinct from the imported agent-runtime model. Decide whether it is a distinct context or overlapping historical material based on the source. | A documented scope comparison and, if distinct, its own import plan. |

E1 -> E2/E3 -> E4/E5 -> E6. E7 can be audited separately; E8 follows the Product/writing scope check. This is a dependency guide, not a requirement to build every platform before importing a bounded candidate.


Progress update: Q1 People and Teams completed in [0072](0072-people-teams-context-import/README.md). Q2 comparison completed in [0073](0073-existing-runtime-gap-review/README.md). People and Teams now runs in the isolated existing-runtime instance verified by [0074](0074-people-teams-runtime-import/README.md). Shared Capability is now imported through the existing runtime in [0075](0075-shared-capability-runtime-import/README.md). Workspace external references and registration are resolved in [0077](0077-workspace-runtime-import/README.md), with exact runtime replay/export verified. Durable Capability State is imported in [0079](0079-durable-state-runtime-import/README.md): the user confirmed that reworked Define no longer needs the old external Invoke requirement. That requirement was removed from the successor; twelve Product Capability requirements remain, native validation and all twelve tests pass, and existing-runtime replay/export is verified. This model is distinct from 0038’s encrypted-object storage model. Next: combine the four isolated runtime package registrations and check source-qualified lookup/currentness and validator integration. Essays follow-up remains queued while its source is being edited.

## Other capability areas — proposed next audit queue

These capability descriptions already exist in the 41-record inventory. Their next model/runtime scope needs an audit; inclusion here does not mean a validator has failed or that a new capability must be invented. Some dependencies may already be carried inside a parent import.

| Order | Area | What it is about | Next concrete result |
| --- | --- | --- | --- |
| Q1 | People and Teams | People, team membership, responsibilities and ownership | Validate/import the model with an empty real-world roster. No actual team is needed. |
| Q2 | Existing runtime gap check | Compare legacy registration, inspection and validation behavior with the Lab runtime | Use the existing Lab event runtime and v4 migration adapters as the target. Compare legacy operations and packages with current coverage; migrate only missing records, adapters or validator integrations. Do not import a second runtime by default. |
| Q3 | Interaction context | Preserve the context needed for an ongoing exchange | Compare the child capability with the imported Agent Reasoning Engine; identify and migrate the distinct remaining context. |
| Q4 | Request governance integration | Receive a direct/gate/block/complete decision around repository work | Audit the child integration's contracts and evidence separately from the parent reasoning engine; keep hook installation as a later operational step. |
| Q5 | Craft ORODI — six capabilities | Offline evidence, denied runtime evidence, canary checks, rollback, lab preparation and commissioning | Audit the six records in dependency order. Start with offline evidence; keep real commissioning separate from importing its capability. |
| Q6 | Lean ontology evidence compiler | Check whether a typed relationship is supported by selected Lean declarations | Validate business/system models, declaration bindings and local compiler evidence. |
| Q7 | Decision gate | Resolve consequential choices with exact decision records | Identify the owned definitions, contracts and evidence; prepare its bounded context import. |
| Q8 | Complexity explanation ladder | Explain a difficult concept through examples without changing its meaning | Audit the explanation capability and retain examples as evidence, not additional capabilities. |
| Q9 | Compiler extensions and residual-path closure | Governed model compilation, typed backends, generated operations, local execution and validation gaps | Compare each imported description with the AlchLang/other parent context snapshots. Import only distinct uncovered models or evidence. |

Source roots for this queue:

- Q1: `../cyberAlchemy-v2/people-and-teams/`
- Q2: `../cyberAlchemy-v2/implementation/ontology-runtime/`
- Q3: `../cyberAlchemy-v2/agent-reasoning-engine/capabilities/interaction-context/`
- Q4: `../cyberAlchemy-v2/development/agent-reasoning-engine/codex-integration/`
- Q5: `../cyberAlchemy-v2/product/craft/capabilities/orodi/`
- Q6: `../cyberAlchemy-v2/product/lean-ontology-evidence-compiler/`
- Q7–Q8: `../cyberAlchemy-v2/review/capabilities/`
- Q9: `../cyberAlchemy-v2/language/capabilities/alchlang/` and `../cyberAlchemy-v2/implementation/domainspec-v2/development/evolvable-validation-framework/`

## Migration-wide gaps already recorded

| Item | Why it remains | Later result |
| --- | --- | --- |
| Larger ontology schema | 0048 and 0063 use a larger candidate schema that has not been admitted. | Resolve the schema contract before claiming those contexts conform to the admitted size limits. |
| D65 full conformance | 0061 imports prototype consistency and request eligibility, not full construction conformance. | A complete evaluator/evidence path, or an explicit supported subset with remaining checks still not evaluable. |
| Define system compiler/runtime | 0063 retains a compiler NOT_EVALUABLE flag and unimplemented runtime. | Resolve compiler evidence and separately plan runtime realization. |
| Routing/session continuation | Session routing remains blocked; Recent Context hooks are uninstalled and task-state restoration is outside its import. | A separately checked continuation design before claiming automatic restoration. |
| Verified Patch live evidence | Offline evidence is imported; historical live-canary receipts remain unavailable. | Fresh exact live evidence if that operational scope is selected. |
| Shared identity and references | Contexts remain source-qualified candidates rather than one globally admitted model. | Reconcile overlapping identities and cross-context references, then validate the combined model. |
| Inventory reconciliation | Current source changes can add or revise packages beyond the frozen 41-capability baseline. | Compare the complete live inventory with imported records; classify additions as capabilities, dependencies, examples or exclusions. |

## Intentionally later

- Definition-card variants/trading/runtime: remains deferred at the user's request.
- Live browser/Wasmtime, production deployment, external services and enforcement activation: later operational scopes, not implied by importing descriptions or contexts.
- Real team setup: unnecessary for importing People and Teams.
- Learn Ontology Experiment: excluded; do not requeue it.
- Reference examples: remain examples; do not promote them to capabilities.

## Evidence and open questions

Baseline: [migration status](MIGRATION-STATUS.md), [41 imported capability descriptions](0035-definition-card-import/imports.json), [latest Essays import](0071-essays-implementation-context-import/README.md), [Essays predecessor material bindings](0068-essays-system-context-import/predecessor-bindings.json).

Confirmed gaps are those recorded in these executions. Q1–Q9 are a proposed first-pass audit queue from the capability inventory and inspected source roots, not a claim that every nested package has been audited. Reconcile the inventory before declaring migration complete. New Essays edits must be assessed as a successor; old test results must not be applied to changed code without checking their inputs.

Runtime clarification: the Lab already has an event runtime, v4 source migration/update adapters, and a graph read-model prototype. The legacy Python ontology runtime is a comparison source, not an automatic replacement or additional runtime. Relevant local paths: `implementation/bindings/ontology-product-event-runtime/v4/`, `product/products/ontology/v1/runtime/`, and `ontology-lifecycle/runtime-candidates/cal-ontology-graph-read-model/v1/`. Exact operational/adoption status is separate from their existence.
