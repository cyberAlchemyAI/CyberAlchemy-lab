# Definitions and records workflow audit

Audited commit: c9c73d9b923bcb7e608c9af24edec68df8e052d6. Runtime implementation: 573932adbe4aaa0d8648bc4900d5a913f184dbca28033ccdfe4a1b64f1038c85.

The migrated current catalog is healthy. This audit identifies nine remaining findings: one Define CLI defect, one authority-documentation drift item, and seven shared Lab guard/operating-model gaps. No production store, source code, admission decision or canonical definition was modified.

## Current state

| Area | Verified current state |
| --- | --- |
| Catalog | 188 current full Definition/v2 records, 377 admitted versions, 189 historical versions |
| Migration | All 183 conversions accepted/admitted/published; the five original v2 bodies reused exactly |
| Folder assets | All four required files exist for all 188 current definitions; 188 renders and 13,536 lineage leaves independently rechecked |
| Historical fidelity | All 194 original admitted body bindings remain exact |
| Runtime | Active, ready, native source current, selector revision 24, native sequence 24 |
| Placement | One shared runtime selection, no runtime code copied into product homes |

The selected model has seven Lab Workspaces: the root Lab plus six product workspaces. There are no selected Project workspace profiles in the current catalog. Craft, Define, Ontology, People and Teams, Lab Website and Trusted Dataset Materialization each have one product home.

    <owning-workspace>/authority/definitions/<readable-name>/<version>/
      definition.json
      DEFINITION.md
      field-lineage.json
      evidence.json

| Owning home | Current definitions |
| --- | ---: |
| Root Lab | 171 |
| Craft | 5 |
| Ontology | 6 |
| People and Teams | 4 |
| Define | 2 |

Shared runtime code remains in implementation/lab-runtime; generic artifact mechanics in implementation/artifact-runtime; shared Definition placement in implementation/lab-workflows/definition-catalog. The migration work plans are evidence/orchestration artifacts, not extra runtime installations.

## Define responsibilities

Implemented in the current AlchLang product: bounded sessions and questions; product-only preparation without invented Project/Work identities; exact catalog discovery and explicit Reuse/Propose/Open/ApplyParameters/ChangeMeaning handling; original-byte source capture and field contributions; source/draft pointer checks; package preparation, frozen inspection, observed confirmation, materialization, reconstruction and replay; complete field-lineage/schema/renderer checks; selective revision; readiness derived from observed original binding facts; typed, version-exact handoff and reported acknowledgement.

The original Python Define engine and predecessor implementation fallback are absent. Generic JSON/schema/file/crypto adapters and the shared Definition renderer remain outside Define. The fresh 41-case Define validation regression suite passes, including modified-package readiness and retained-request divergence checks.

Owner acceptance, authenticated consumer acceptance, construction enforcement, native permissions and canonical admission remain outside Define. A reported lookup or acknowledgement does not grant those authorities.

## Shared Lab responsibilities

Implemented: workspace/runtime selection; generic registered Record/Artifact Type/Definition creation guards; native schema/identity/project/scope checks; exact owner-disposition and authorization bindings; signing and verified issuance; seven-stage construction entry; original native apply/recovery; atomic snapshot selector publication and native-effect closure; retained body/owner/lifecycle evidence; authenticated join history and original-operation reconciliation; v1/v2 compatibility and source carry-forward; declared impact closure; executable independent conformance; trusted source selection; readable definition placement; runtime data recovery without keys/runtime copies.

The native store contains 640 artifact-instance versions, 144 Artifact Type versions and registered record mechanisms as well as the definitions. These totals include imported and derived governance state. The 24 post-genesis operations on the new branch transfer the original five v2 definitions/Registry contract and admit the 183 conversions; they do not demonstrate new product/work record journeys across every product workspace.

## Remaining findings

Priorities: P1 protects the authority/layout publication boundary; P2 completes operating flows or fixes a bounded CLI defect; P3 corrects live guidance. Reproduced findings below used pure operations, read interception or disposable data copies.

### D-01 (P2, Define): Piped AlchLang source export exits successfully with truncated output

**Observed:** Actual sources response is 146176 bytes; the source asset is 308581 bytes; exit status is zero.

**Required contract:** Reuse the complete stdout/byte-preserving response contract for every exporting CLI command.

**Next:** Await stdout completion and verify exact byte/hash equality for a piped sources response. Generic transport only; no Define business rules move out of AlchLang.

Evidence: DEFINE-TRANSPORT-PROBE.json.

Source anchors: workspaces/products/define/implementation/cli/alchlang/runtime/cli.mjs:59.

### D-02 (P3, Define and Lab documentation owners): Active documentation still calls three admitted definitions unadmitted

**Observed:** The 44-entry Define design selection has three candidate-unadmitted labels whose exact bodies are admitted-current: Lab Workspace, Definition Pack and CyberAlchemy Define. All 44 selected paths still exist. The other pinned versions may validly remain historical semantic dependencies.

**Required contract:** Explicit historical as-of selection versus current authority lookup; no new admission decision.

**Next:** Keep original decisions and pinned meaning bytes; update live guidance/current standing resolution and annotate historical design snapshots.

Evidence: INVENTORY.json.

Source anchors: workspaces/products/define/README.md:13, workspaces/products/define/work/development/alchlang-only/DEFINITIONS.json:1, implementation/lab-runtime/alchlang/shared-records/README.md:74.

### L-01 (P1, shared Lab): Catalog readers do not authenticate publication receipts

**Observed:** On a disposable SQLite backup, changing the latest publication receipt makes verified inspection fail publication-retained-evidence-corrupt. readPublishedCatalog still returns 377 versions and 188 current entries.

**Required contract:** Verified catalog observation bound to selector, authenticated publication history and exact snapshot; reported discovery remains distinct from semantic acceptance.

**Next:** Use trusted publication verification or an equivalently authenticated snapshot proof before exposing admitted standing. Keep this trust check in the Lab reader, not Define semantics.

Evidence: PROBES.json:catalog_after_corrupted_publication.

Source anchors: implementation/lab-runtime/alchlang/shared-records/catalog.mjs:7, implementation/lab-runtime/alchlang/shared-records/runtime.mjs:118.

### L-02 (P1, shared Lab): A new publication can opt out of workspace layout validation

**Observed:** verifyLocations accepts the actual 377-entry current registry after locations, layout and layout_protocol are omitted, performing zero location reads. The publisher has no separate trusted mandatory-layout policy.

**Required contract:** Trusted, nonregressing workspace layout policy for new publications, with explicit historical-read compatibility.

**Next:** Require the active layout independently of producer declarations; retain explicit historical reads for older valid snapshots.

Evidence: PROBES.json:layout_protocol_omission.

Source anchors: implementation/lab-runtime/alchlang/shared-records/locations.mjs:18, implementation/lab-runtime/alchlang/shared-records/runtime.mjs:86.

### L-03 (P1, shared Lab): The four-file definition directory is not a complete bound publication unit

**Observed:** The current snapshot contains all 188 readable bodies, 183 readable Markdown paths, zero readable field-lineage paths and zero readable evidence paths. Location validation passes with lineage/evidence reads blocked. All four files do exist in every current physical directory and current Markdown renders correctly. Five existing v2 projections retain historical bindings.

**Required contract:** A per-version Definition directory manifest binding body, deterministic projection, full field-lineage and referenced evidence, including readable location aliases for retained originals.

**Next:** Bind and validate all required assets; preserve original body/projection evidence and require verified package/lineage facts. Existing placement retries must check evidence.json too.

Evidence: PROBES.json:four_file_contract and CATALOG-VERIFICATION.json.

Source anchors: implementation/lab-runtime/alchlang/shared-records/locations.mjs:5, implementation/lab-workflows/definition-catalog/cli.mjs:28.

### L-04 (P2, shared Lab): Ready status does not attest canonical filesystem mirrors

**Observed:** Operational readiness remains ready while reads of authority/definitions/current.json and every current directory Markdown/lineage/evidence file are blocked in-process. It attempts none of those reads. The real live files are currently valid; no live file was changed.

**Required contract:** Separate or combined view-reconciliation readiness covering canonical selection, workspace manifests and generated indexes, plus recovery after publication/view-update interruption.

**Next:** Expose filesystem/view health explicitly and reconcile public current.json/index/catalog projections against the selected signed snapshot without rewriting frozen legacy registry.json.

Evidence: PROBES.json:readiness_without_canonical_mirrors.

Source anchors: implementation/lab-runtime/alchlang/shared-records/readiness.mjs:9, work/plans/definition-canonical-migration/finalize-layout.mjs:1.

### L-05 (P2, shared Lab): Routine handoff-to-admission orchestration remains migration-specific

**Observed:** Generic review, construction, native apply, publication, joins and recovery exist. The successful complete driver is under the 0077 work plan, with fixed accepted target set and batch assumptions; no maintained consumer of PreparedHandoff/ReportedHandoffResponse was found. Placement unconditionally preserves current meaning/owner/name. Home assignments are pinned into the implementation closure.

**Required contract:** Reusable package/handoff consumption, explicit owner decisions, governed home assignment, reviewed v2 successor/meaning change and custody/name evolution, durable publication and acknowledgement correlation.

**Next:** Promote the orchestration into a maintained Lab workflow driven by actual accepted inputs/current authority. Keep representation-preserving import strict and add separate reviewed evolution routes; do not create another runtime or put construction enforcement into Define.

Evidence: OPERATIONAL-PROBES.json:meaning_preserving_placement and source inspection.

Source anchors: implementation/lab-workflows/definition-catalog/cli.mjs:20, implementation/lab-runtime/alchlang/shared-records/implementation.mjs:20, work/plans/definition-canonical-migration/migrate.mjs:1, work/plans/definition-canonical-migration/refresh.mjs:6.

### L-06 (P2, shared Lab): Impact is complete only for a hand-selected consumer graph

**Observed:** The qualified universe has 388 subjects. Every one of its 377 Definition-version nodes has dependencies: []; the builder adds registry, two readers, runtime closure and seven workspace profiles. This is not a discovered whole-Lab dependency projection.

**Required contract:** Governed dependency projection and coverage receipts for definitions, carrier/schema/generator/lineage consumers, records and other actual downstream users; explicit meaning of dependency edge kinds.

**Next:** Reuse ontology relations and source bindings to build and verify the declared graph, distinguish provenance from normative dependency, and report omitted/unresolved consumers rather than assuming whole-Lab closure.

Evidence: INVENTORY.json.

Source anchors: work/plans/definition-canonical-migration/refresh.mjs:14.

### L-07 (P2, shared Lab and owning workspace record authorities): Workspace metadata and generic record primitives are ahead of complete business-record operating flows

**Observed:** Define, People and Teams, and Lab Website profiles have primary_subject.ref null. The real product-only Define context resolves without a store, then refuses native-project-context-mismatch with the active native store. Generic create emits RecordOutputs to an explicit caller output; the shared published catalog is Definition-specific. The native store contains 640 artifact-instance versions and registered record/type mechanisms, largely imported or derived; the 24 new branch transactions target definitions and Registry/v2, not a new product/work record rollout.

**Required contract:** Bindings to existing/admitted business instances, workspace/native-host context bridge, per-kind record custody/output rules and verified product/project/work record journeys.

**Next:** Reuse already bound Craft/Ontology/other assets and admit only genuinely absent records through their owners. Support workspace-native routing or an explicit host-project bridge without inventing Projects for product-only preparation or copying runtime code.

Evidence: OPERATIONAL-PROBES.json and INVENTORY.json.

Source anchors: workspaces/products/define/WORKSPACE.json:9, implementation/lab-runtime/alchlang/shared-records/native_port.py:32, implementation/lab-runtime/alchlang/ports/creation.py:83, implementation/lab-runtime/alchlang/shared-records/catalog.mjs:7.

## Verification and limits

Fresh audit evidence:

- STATUS.json: actual central shared status; ready/current on the selected implementation.
- DEFINE-DOCTOR.json: current Define AlchLang source and pinned toolchain.
- DEFINE-VALIDATION.json: 41 current validation/regression cases, all PASS.
- CATALOG-VERIFICATION.json: all 188 schemas/renderers, 13,536 exact lineage leaves and 194 original body checks PASS. CATALOG-CHECK-SOURCE.json records reuse of the existing independent checker with output redirected here.
- PROBES.json: actual layout-omission, sibling-binding, readiness-view and disposable corrupt-publication reader results.
- OPERATIONAL-PROBES.json: actual product-only context/native-host mismatch and pure meaning-preserving placement restriction.
- DEFINE-TRANSPORT-PROBE.json: actual public piped sources truncation, zero exit.
- INVENTORY.json: current authority, all 44 Define design bindings, declared impact graph and actual native record inventory.

The earlier 84 native, 227 shared decision, 20 integration, 19 publication, 19 hardening and other migration qualifications remain retained evidence at their recorded source cuts/implementations; this audit did not relabel or rerun every one of those suites. Current source selection/readiness was freshly verified. Full restore qualification remains the committed migration evidence; no restore into live data was attempted.

## Definitions and contract coverage

No additional missing global Definition was demonstrated by this audit. Lab Workspace, Definition Pack and CyberAlchemy Define are already admitted exact bodies. Their stale candidate labels are documentation/as-of-selection drift, not three new approval blockers.

Before fixes, reuse the existing meanings for Definition, Artifact, Schema, Source, Provenance, Traceability, Lab Workspace, Product, Project, Work and Contract where applicable. Complete the specific reader, directory-manifest, publication-policy, mirror-reconciliation, lifecycle/handoff, dependency-coverage and record-host contracts identified above through definitions -> artifacts -> ontology -> business-system bridge ontology -> system ontology -> AlchLang -> generation. New global meanings require Define only if existing definitions do not cover the intended semantics.

Recommended order: L-01/L-02/L-03, then L-04 and D-01, then L-05/L-06/L-07. Correct D-02 guidance without rewriting original decisions, pinned semantic evidence or historical receipts.

## Definitions Governance Summary

- Definitions updated: none.
- Index synced: not applicable; current indexes were audited without mutation.
- Drift found: yes, current authority annotations and missing ongoing view-health enforcement.
- Undefined critical terms: no new missing global definition established; this is not a whole-repository vocabulary proof.
- Conflicting consumers: one confirmed Define current-standing guidance group plus stale shared activation/count/launcher guidance.
- Validation: current catalog and 41 Define cases PASS; isolated negative probes expose the listed open guard gaps.
- Follow-ups: the nine owner-separated items above. No fixes, admissions or runtime activations were performed.
