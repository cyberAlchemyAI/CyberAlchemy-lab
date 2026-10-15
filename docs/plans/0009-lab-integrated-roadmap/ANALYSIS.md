# Whole-Lab milestone analysis

Status: proposed analysis, 2026-10-07. Authority effect: none.
Scope: all five milestones in [the roadmap](../../ROADMAP.md), including their implementation dependencies. This is repository analysis and planning; new implementation, runtime validation, admission and provisioning are future tasks.

## 1. L0 — Foundation and controlled proof

### Objective and current result

Establish that meaning, exact authority, durable state and ephemeral context can support one bounded operational transaction. D70 admits the integrated model and its exact contract set. D71–D73 establish operational roots, histories and a first governed Agent episode. D74 supplies the transaction governance surface. D75 admits runtime v1, with its original D74 source profile preserved.

The scope is important: the repository is at D75; admitted v1 reads its frozen D74 envelope. Candidate v2 integrates D75 and its existing receipt records 38 passing checks plus a disposable Work/context demonstration. Neither implementation proves the complete Lab Product, a general Agent executor, or a live service.

### Implementation analysis

The Python runtime already resolves heterogeneous carrier identities, validates current contracts, generates stable Decision cores and paired histories, commits immutable local transactions through an atomic HEAD, verifies Ed25519 approvals, recovers recognized interrupted writes and generates bounded context. It has a real CLI and three inspection lenses. These mechanisms should be reused.

The remaining foundation work is reconciliation rather than reconstruction: bind current evidence, account for historical candidate labels through admission overlays, preserve the D73 exact-version diagnostic, and map older Plan 0007 obligations to Plan 0008's delivered code. A registry entry establishes a contract; it does not establish workflow implementation or complete referential closure.

### Inputs, output and acceptance

- Inputs: exact Decisions, bundles, registry/schema bindings, source profiles and existing receipts.
- Output: the source baseline and contract coverage inventory in this planning package; a scoped foundation checkpoint in the DAG.
- Acceptance: distinguish repository admission, selected executable profile, local store state and derived projection state; expose every selected unresolved mapping.
- Failure conditions: source drift; selecting a current schema for an incompatible historical record; interpreting candidate-body status as effective admission; treating package labels as artifact endpoint versions.
- Cost: low for reconciliation; high only if a specific admitted contract requires correction. No broad vocabulary expansion is justified by counts alone.

**After this layer, we know whether** the bounded foundation works. That result is established within the cited v1 scope. B00 carries it as scoped evidence; B01 records this new planning analysis.

## 2. L1 — Repeatable real local operation

### Objective

One real Work cycle must survive an authority change, restart and fresh Agent session. The same executable should accept independently reviewed compatible source profiles. Historical branches must remain recoverable and exact.

### A. Profile continuity — C01, C02, C04, C05

**Observed implementation:** CLI reads package `profile.json`; `Store.initialize` requires equality with that package profile; replay marks another profile stale. `capture` hashes the mutable current-State lookup against a frozen selection. `freshness` also detects a new admission epoch. Thus admitting another package can immediately stale the selected profile. Candidate v2 demonstrates explicit D75 integration but retains this structural coupling.

**Recommended construction:** put source-profile data behind a closed, versioned protocol and an explicit reviewed-selection mechanism. The executable declares compatible protocol/generator versions. A profile pins immutable roots, registries, schema selectors, exact State/history selection, local ontology signatures and the source allowlist. The generated current lookup is a consistency/freshness hint, never the authority anchor. Profile review metadata belongs to its exact package/envelope; using an existing canonical carrier requires a fit decision, not an invented `Source Profile` Artifact Type.

**Transition rule:** preserve the old local branch; capture the selected new baseline; generate a transition proposal listing retained, promoted, revalidated, conflicting and excluded local results; review its exact effects; create a separately identified successor branch. Link the branches with exact evidence under declared contracts. Never edit a committed transaction's baseline or copy old signatures as authorization for new effects. If the new repository baseline already contains a promoted result, do not admit it twice.

**Acceptance:** the executable remains byte-exact across two compatible reviewed profile selections; old stores remain readable as historical; unsupported versions, missing grants, drift, changed HEAD and ambiguous revisions block current writes. A fresh successor branch reconstructs approved continuity without silently claiming the old branch current.

The admission itself can advance the repository baseline. C01 must specify stable profile-policy cores and whether the resulting exact capture is an already declared deterministic consequence or a separate reviewed profile change. A profile cannot require an impossible digest of its own enclosing admission; deterministic profile bookkeeping should not create another owner approval boundary.

### Typed extension rule enforcement — C14

`validate_relation` checks ordered endpoint pairs, exact endpoint identity/revision and a closed object of qualifier fields. `prepare` rejects a duplicate axis ID and requires current endpoint carriers and directional roles for added pairs. These are reusable structural checks. They do not establish all obligations in the D64-admitted Typed Connection Extension Rule: preservation of the unique semantic question, pair-specific value domains and cross-qualifier constraints, and one canonical writable relation authority. For example, the inspected `realizes` qualifier contract uses nonempty strings for `realization_role` and `exact_target_version_ref`; that alone does not demonstrate a closed pair-specific role domain.

C02 maps the complete normative obligations and exact schema fit. C14 implements the missing admissibility checks and binds explicit semantic review evidence where a judgment cannot be reduced to a structural test. If a current carrier cannot express the necessary contract, propose an exact successor within the same reviewed package. A specialized relation carrier and its generic Typed Relation projection cannot both accept independent writes. No new semantic Definition is needed merely to restate this already admitted rule.

Acceptance includes rejection of inferred Cartesian pairs, semantic duplicates with fresh axis IDs, open pair qualifiers and duplicate writable authorities. Existing historical contracts are not silently rewritten; the selected extension scope and any required successor effects are reviewed explicitly.

### B. Replay efficiency — C03, C06

**Observed implementation:** every `Store.replay` walks genesis through HEAD, stages targets, checks signatures, regenerates consequences and checks projection digests. `Session.context` invokes replay on every access; notes call context first. `freshness` hashes captured source material. This supplies strong validation but repeats work. The v2 suite's 1,102.787 seconds is not an operation-latency measurement.

**Recommended construction:** first separate and measure capture, file hashing, schema validation, replay, graph construction and session access at defined transaction counts. Preserve an uncached full verifier. Start with process-local reuse of previously verified work under exact HEAD/configuration/baseline/generator/schema and complete relevant byte bindings. Metadata such as mtime alone is insufficient. Cross-process checkpoints require a separately specified trust/verification path; a self-digest alone cannot prove past approvals or consequences.

**Acceptance:** accelerated and full paths yield identical state and histories; alteration of an old transaction, source, approval, schema, configuration or checkpoint never becomes trusted current state. Report timings and environment against thresholds declared before evaluation. If acceleration adds no sufficient value, record a measured no-op decision instead of adding cache complexity.

### C. Local results and repository promotion — C07

**Observed implementation:** local transactions explicitly declare no repository admission effect. D75's repository publisher builds one exact decision-specific admission bundle, publishes it by directory rename and rebuilds mirrors/current lookup. It is not a generic promotion API. It also deliberately checks absence of the default permanent store.

**Recommended construction:** a reusable promotion proposal exporter selects exact committed local targets, their contracts, evidence, branch HEAD and source baseline. It independently checks current repository authority and constructs stable repository Decision cores. A generic publisher stages a complete immutable bundle, validates all consequences and exact authorization, then commits once. Generated mirrors are recoverable projections. Owner conversation authorization and operator cryptographic authorization remain distinguishable mechanisms.

**Acceptance:** selection adds no unrelated private/session material; stale repository baselines and identity conflicts block; one exact owner response may resolve multiple independent cores; no extra decision is requested for deterministic consequences. Local signatures do not silently authorize repository effects. Recovery can reconstruct mirrors from the immutable committed bundle.

### D. Context provenance and real use — C08–C13

**Observed implementation:** context generation is schema-valid and disposable, but it contains literal implementation/profile/classification/assignment reference labels. The inherited Generated Output uses a literal v1 generator label. Schema validity does not by itself prove those references bind exact admitted subjects or confer permissions.

**Recommended construction:** audit each reference as governed, historical, local-protocol or unresolved; bind actual implementation revision and generator package separately; supply selected durable owner/profile/assignment evidence where required. Keep a read-only context consumer distinct from a delegated action executor. L1's real task may be human-executed with Agent-assisted inspection; general Agent action enforcement belongs to W02.

**Operational sequence:** complete candidate construction, selected typed extension enforcement and isolated evidence; show its realistic example; obtain the exact admission decision; provision only the explicitly selected operator/store; complete real work and review its supported evidence. Persist an Operational Lesson only when observations justify one. Close the session, restart and reconstruct approved state. Do not manufacture an Incident or a beneficial lesson result to finish a checklist.

**Acceptance:** closure distinguishes completed Work from a planned Work demo; persists selected evidence and authority, not working memory; the next Machine Agent has a new session identity and obtains fresh views. Process-interruption guarantees remain scoped; power-loss and multi-host claims need additional evidence if later selected.

**After this layer, we know whether** real local operation remains trustworthy across change. C13 is the milestone join. Main cost drivers are continuity, promotion/recovery integration and verification; broad migration and a network service remain deferred.

## 3. L2 — Integrated work and learning

### Objective and implementation boundary

Exercise existing schemas as a coherent system. The examined local runtime has generic governed record writes and read-only Agent context. It has no general workflow runner, policy/delegation interpreter, tool executor or lesson selection/application service in its CLI/module surface. Existing ontology executors serve other explicitly bound source contracts and cannot be treated as these Lab workflows without adapters and evidence.

### A. Workflow contracts — W01

Normalize domain rules as an implementation layer over current carriers. Define workflow states, allowed transitions, actor roles, satisfaction checks, reference closure and failure behavior. Do not overload one `status`: domain completion, admission, implementation conformance, runtime observation and Product outcome remain separate.

Inputs are Intent, Intent Resolution, Goal, Product/Project identity, Coordination Context/v2, Work and current contracts. Coordination Context retains its single `goal_ref`; a Work may refer to multiple goals only where its contract permits it. Resolve each schema selector and every reference before designing adapters. Decisions select exact subjects/satisfaction checks; completion requires observations and an assessment.

### B. Actors and actions — W02

Reuse the local owner signature for its bounded transaction scope. Add a separate bounded action evaluator using Principal/Role Assignment, Delegation, Agent Assignment, session, Tool contracts, period, revocation and explicit approval gates. Evaluate the whole requested action at execution time; denied, expired, revoked, unknown or ambiguous authority prevents dispatch. Redelegation defaults to the declared contract, never inference from graph adjacency.

Dispatch through a selected local tool adapter with exact inputs and environment boundary. Capture receipt, output and residue under Agent Action. Unknown completion after interruption remains indeterminate until reconciled; do not retry a non-idempotent action without a documented reconciliation/compensation rule. No automatic owner credential access, network service or general organizational IAM is implied.

Machine Agent instances remain session-scoped. Persist eligible audit evidence and closed-session facts under review; do not persist short working memory or reuse a continuing Agent identity across sessions.

### C. Engineering and research — W03, W04

Engineering runs Intent -> selected Work -> Define/Design/Plan -> bounded implementation action -> exact output/evidence -> Work Outcome Assessment. These workflow stages do not invent global relation names. Build Typed Relations only from declared endpoint pairs/qualifiers, with exact revisions and roles on both carriers.

Research runs Research Inquiry/Hypothesis -> Experiment Design -> Experiment Run or Research Run -> Measurement Result/Observation -> Finding/Evaluation. Experiments can be connected to research, Product, Project, capability or implementation only where current Relation Kind signatures allow the exact pair. A missing connection becomes an explicit extension proposal rather than a catch-all relation. A negative or inconclusive experiment remains a useful result; execution is not hypothesis confirmation.

Use two concrete cases: correct an exact-version reference under a bounded engineering task, and compare replay approaches under a research/experiment task tied to the Lab capability. Thresholds/methods and intended interpretation are declared before measurement. These cases are proposals for later execution, not completed experiments.

### D. Evidence, failure and challenges — W05

Build attributable observations and Evidence Sets; distinguish observation from Finding and assessed confidence. Classification Scheme/Value/Assignment describe meaning independently of admission or completion. Failure Occurrence records manifested boundary violation; Failure Assessment separates mode assignment, cause hypotheses, impact, containment, recovery and uncertainty. A Failure Control Binding states control intent, not proven efficacy. An Incident needs its own declared threshold and evidence.

Challenge handling binds a Challenge Event to exact subject revision and contract, checks challenger eligibility, records evidence and response deadlines/obligations, and links any resolving Decision. Submit/resolution/governance-only changes must not silently mutate semantic content. Exact ontology challenge joins are delivered at O02.

### E. Operational learning — W06

Build lesson drafting and explicit review using evidence, applicability, exclusions, counterevidence, falsifier, retention policy and expiry. Context selection filters current lessons by applicability, unresolved challenges, expiry and conflicts, while exposing why each was selected or omitted. Selection is not application.

Record Lesson Application against an exact lesson revision and session. Outcome Assessment records predicted/observed results and causal claim ceiling. Improvement Signals/Targets propose follow-up work. Promotion is an explicit effect after appropriate evidence, never automatic because a lesson was used once.

### Exit and costs — W07–W09

Integration evidence must cover engineering, research, a denied/expired action, evidence lineage, classification, a bounded failure/challenge case, and subsequent lesson application with an assessed result. A controlled negative scenario is labeled controlled; it is not a production incident. Review the combined workflow package once with independent declared effects; then exercise selected real cases under the operational scope and close them.

**After this layer, we know whether** the contracts support useful governed work and learning. W09 is the milestone join. Main costs are domain transition rules, authority enforcement, reference closure and realistic evidence. Exhaustive domain automation and automatic lesson promotion remain deferred.

## 4. L3 — Coherent ontology and controlled migration

### Objective and available implementation

The Rust ontology lifecycle library already represents separate semantic/governance streams, exact joins, typed properties, challenges, cuts and context projection. The graph candidate already has bounded traversal, immutable generations, disposable checkpoints and tail recovery under its own canonical-event contracts. The v4 source runtime already has exact allowlisted package adapters and durable local event transactions. These are different responsibilities and authority envelopes.

### A. Mapping design — O01

Declare a selected Lab ontology profile: exact artifact revision -> Ontology Node; exact Typed Relation -> global-projection Edge; admitted local signature -> local-interpretation Edge. Preserve source identity, carrier revision, representation identity and namespace. Map each axis independently. Every bridge to code requires business-side and system-side evidence; a function label alone does not establish capability realization.

This design can proceed after B01. It provides earlier queries without claiming L3 closure or depending on every L2 workflow being finished.

### B. Lifecycle and query adapters — O02, O03

Adapt selected Lab admission envelopes to canonical ontology representation events. Preserve separate cursors and exact semantic tuple joins. Node retire/remove/withdraw semantics are explicitly mapped, not equated. Project history and ontology history are different streams; ontology projections must cite their Lab inputs and own representation events without claiming copied Project events are ontology-native events.

Generate deterministic exact cuts/views. Rebuild from source events and compare Python inspection paths with the selected Rust adapter's output, where adopted. Governance-only challenge changes update joined governance state without semantic mutation. Optional Rust graph acceleration follows parity evidence, not technology preference; a Python implementation that meets the chosen scope can satisfy the query obligation.

Queries must answer meaning, exact contract, admission, source, implementation/evidence and missing pieces. Cover Authority, Provenance and Lifecycle, actual edge directions, bounded depth, exclusions, historical revisions and stale inputs. Keep unmapped subjects and unresolved versions explicit. Plan 0007's older C2 frontier is reconciled against delivered Plan 0008 mechanisms, not restarted wholesale.

### C. Migration — O04, O05

Select a useful domain slice rather than assuming every legacy file belongs in the Lab. Capture repository identity/revision where available, exact paths/bytes, dependency edges, public/private classification and source disposition. Each item is imported/adapted, referenced externally, deferred, excluded or blocked with a reason.

Reuse v4's source-qualified mappings and existing importers where contracts fit. The v4 common source-record envelope proves digest/envelope validity, not every domain schema or transitive closure. Validate selected records against the exact intended Lab carriers; report unsupported source references rather than aliasing them. Preserve original sources. Produce one exact import/adaptation proposal with selected records, evidence and necessary typed extensions.

### Exit and costs — O06, O07

Review exact ontology/adaptation/import effects together where practical; no view rebuild needs a new authority decision. Reconstruct the selected domain from canonical sources, prove joins/parity/freshness, and account for every selected migration item and outstanding gap. Historical adoption or execution remains evidence for its own scope, not live activation of a new Lab adapter.

**After this layer, we know whether** the selected Lab scope is coherent and explainable across source, authority, ontology and implementation. O07 is the milestone join. Main costs are semantic mapping and source reconciliation. Source retirement, broader imports and unselected services remain separate future scopes.

## 5. L4 — Usable Product and stable release

### Objective and existing Product boundary

The operational foundation declares the Governed Knowledge Lifecycle capability. Its source body contains an empty realization-binding list and untested value hypothesis; effective instance admission does not prove fulfillment or usefulness. The CLI is usable for bounded inspection/transactions, but complete Product UX, supported installation/upgrade and pilot evidence remain to be built.

### A. Product scope and packaging — R01, R02

Define users, supported environments, selected interface, expected outcomes and acceptance measures. R01 can start after B01; planning users and outcomes does not wait for full ontology integration. Start with one coherent CLI surface, unless an explicitly reviewed requirement selects another interface. UI/MCP/network services are not automatic requirements.

Package exact dependencies and executable/profile compatibility. Design fresh install, export, versioned upgrade, profile transition, recovery and rollback with private keys/runtime state outside Git. Failed installs preserve recoverable state. An export must identify its authority/branch, source bindings and excluded private material; an import requires independent review of its effects.

### B. Interface and realization — R03, R04

Expose currentness, exact scope, independent state facets, unresolved gaps, proposal diff and declared effects in user language. Keep code/tooling details in inspection surfaces unless they affect the user's decision. Provide dry review, one clear decision boundary and explainable receipts.

Select exact Capability Realization Bindings for actual realizations. Binding admission, owner-local adoption, conformance, observed runtime behavior and value assessment have separate evidence. Do not create one binding per arbitrary code file or assume one admitted Implementation fulfills every capability. A selected binding can list multiple realization endpoints where its contract permits.

### C. Pilot, privacy and release — R05–R08

Run a bounded real pilot with declared baseline/methods and record work completion, state findability, context boundary preservation, learning outcomes and operational costs. Report regressions and negative evidence. Complete the private/public boundary review against the exact selected release package, including evidence provenance, local stores, credentials, caches and imported source classification.

Validate deterministic packaging, supported install/upgrade/recovery, whole-loop examples, contract/relation alignment, layer deferrals and release evidence. Every included admitted artifact has a matching exact validation binding. Produce an exact candidate manifest and show the reviewed example before the owner release decision. Publication and deployment occur only if included in its authorized effects.

**After this layer, we know whether** the bounded Lab is useful and operable enough for stable v1.0.0. R08 is the release decision node. Main costs are installation/recovery support, UX, pilot evidence and release validation. No calendar or performance threshold is invented by this plan.

## Cross-layer architecture and dependencies

| Boundary | Implementation responsibility | Must not absorb |
| --- | --- | --- |
| Contracts and exact source profiles | Identity/schema/endpoint/selector and compatibility rules | Admission or inferred permission |
| Pure proposal and consequence engine | Closed targets, stable cores, deterministic postimages | Operator credential custody or publication side effects |
| Authority adapters | Exact local/repository owner effects and bounded Agent action evaluation | Domain satisfaction or Product value |
| Store/publisher adapters | Atomic commit, history retention, recovery, promotion transport | Silent rebases or mutable historical inputs |
| Workflow layer | Domain transitions, evidence, lessons and application | Automatic authority from successful execution |
| Ontology/read layer | Exact representation, joins, coverage, views and explainable queries | Canonical subject meaning or replay authority from a cache |
| Product surface | Selected user workflows, installation and value assessment | Unselected services or broad migration claims |

Every milestone has verification and review nodes. Product and ontology design begin in parallel with L1 where dependencies permit. Later joins require their operational evidence. Duration-based critical-path calculation waits for scoped estimates; the DAG presently encodes dependency order and qualitative cost, not promised dates.

## Planning limits and unresolved decisions

The analysis covers every roadmap milestone and inventories every current registered carrier and Relation Kind. It is not a fresh conformance evaluation of every historical artifact instance, a live service audit or a completed migration inventory of all external repositories. Implementation readiness is bounded by the named task's inputs and design decisions.

Open choices are recorded in [the decision ledger](work-pack/shared/cross-task-decisions.md): profile review carrier fit, successor-branch authority, replay acceleration trust boundary, action adapter permissions, selected ontology domain/import scope, interface and release scope. They have assigned design tasks and do not block creation of this plan. Execution resolves each before its dependent implementation proceeds.
