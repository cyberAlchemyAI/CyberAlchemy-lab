# Shared Lab definitions and records: candidate design

This package designs the six remaining shared Lab integrations in AlchLang before active implementation. It starts from the five exact pending Definitions and retains existing Define behavior, native governance, and one shared runtime. No candidate is admitted, no owner response is invented, no runtime is copied or activated, and no source profile is repinned.

## Start with the actual source state

Two earlier audit conclusions were incorrect. Decision 0070 already admits the Definition/v2 **carrier**, and both the public creation wrapper and compiled CreateDefinition policy already select v2. Carrier admission admitted zero ordinary Definition instances. The canonical registry still uses its v1 contract and holds 189 admitted exact versions, selecting 183 current identities. The gap is reviewed mixed-version registry publication and consumer adoption, rather than another v2 carrier admission.

The current five pending ordinary Definitions remain outside that registry. Their original files are unchanged. A candidate's lifecycle label inside its payload, a carrier's current standing, a canonical registry selection, and native source standing are independent facts.

| Pending exact meaning | Proposed treatment | Actual outcome |
| --- | --- | --- |
| Lab Workspace, 2.0.0-candidate.1 | Reuse durable Product/Project workspace meaning; bind current realization externally | Owner review pending |
| Definition Pack, 1.0.0-candidate.1 | Reuse normative meaning; offer candidate.2 correcting old consumer/context references | Owner selects exact original or successor |
| CyberAlchemy Define, 1.0.0-candidate.1 | Reuse normative capability meaning; offer candidate.2 correcting old realization and live-adoption claims | Owner selects exact original or successor |
| Construction Chain Contract, 1.0.0-candidate.1 | Reuse seven-stage/six-handoff meaning | Owner review pending |
| Construction Stage Handoff, 1.0.0-candidate.1 | Reuse exact adjacent-stage, subject-bound handoff meaning | Owner review pending |

See FIVE-DEFINITION-REVIEW.json, OWNER-REVIEW-REQUESTS.json and DEFINITION-SUCCESSOR-PROPOSALS.json. The two successor proposals preserve the decoded scientific/formal voice, boundaries and scope; explanatory context and metadata change. Their human projections are generated with the existing Definition/v2 artifact generator. They are authored proposals, not admitted or CLI-materialized Definitions. Old review requests cannot approve successor bytes.

The Define CLI journal records source-backed candidate assessments and open handling. Its one-active-question model groups five independent owner-review requests into one unanswered question. Context sufficiency is a declared bounded assessment for design and asking questions; it grants no semantic or effect authority. DEFINE-PROCESS.json records the actual CLI outcome and replay.

## Follow the chain

Definitions → artifacts → ontology → business-system bridge ontology → system ontology → AlchLang → generation.

1. **Definitions:** DEFINITION-SELECTION.json reuses existing admitted meanings and identifies five pending exact targets. Semantic owner decisions remain required before selecting those candidates as canonical authority.
2. **Artifacts:** ARTIFACT-CONTRACTS.json, COMPATIBILITY-MATRIX.json and contracts/ define exact review, compatibility, registry, context, creation, publication, journal, impact and construction evidence shapes.
3. **Ontology:** BUSINESS-MODEL.json separates identity, meaning, applicability, owner disposition, permission, source standing and execution outcome. These authored design models are not an admitted live Ontology Cut.
4. **Bridge:** BRIDGE-MODEL.json maps business obligations L-01 through L-06 to actual existing support, proposed AlchLang decisions and missing ports.
5. **System ontology:** SYSTEM-MODEL.json and PORT-CONTRACTS.json assign observations, persistence and effect boundaries. Original bytes, schema, role, scope, signatures where applicable, source cut and HEAD must be independently verified by future real adapters.
6. **AlchLang:** alchlang/contracts.alch, semantics.alch and design.alch declare the candidate contracts, rules, policies, calculations, operations and join lifecycle.
7. **Generation:** GENERATION-RECEIPT.json and DESIGN-VERIFICATION.json bind genuine compilation and synthetic pure-plan checks. They establish candidate technical behavior, not actual authority or full-chain conformance.

CHAIN-HANDOFFS.json binds the six adjacent candidate design handoffs. These records expose subjects, transformations, coverage obligations and unresolved review; they do not claim accepted implementation handoffs. A file-source vector does not replace event/cursor evidence required for a live Ontology Cut.

## Definition/v1–v2 compatibility

**Read retained v1 with its exact v1 schema and generator; create new v2 candidates under the already admitted v2 carrier; upgrade a historical body only as a separately reviewed exact successor.**

V2 is not a strict superset. Both carriers require the same 22 top-level fields, but carrier/schema/generator bindings change. V1 has four typed relation kinds. V2 has 23, retains three old kinds, adds twenty and removes relation.supersedes. Never silently rename supersedes to successor-of, drop relations, downcast v2, overwrite changed bytes under the same (definition_id, version), or infer withdrawal from lineage.

An upgrade requires original-body lineage, verified exact schema/generator bindings, explicit relation mapping where needed, unchanged meaning or an explicit meaning-change review, and the exact owner's disposition. Relation mapping alone does not authorize an upgrade.

The proposed Registry/v2 selects carrier/schema/generator and owner evidence **per entry**. There is no global default that relabels existing v1 entries. It preserves original bodies, decisions, current selections and retained versions unless an explicit lifecycle transition changes them. JSON Schema cannot prove these semantic invariants.

The existing Registry/v1 contract is embedded in artifact-type/v1 and points to foundation/v1/schema.json at #/$defs/definitionRegistry; V1-REGISTRY-CONTRACT.json records the exact descriptor, schema and existing effective-registry entry. A separate directory is unnecessary. Its historical schema describes bootstrap candidate posture; subsequent actual publication decisions govern the admitted registry. Registry/v2 must explicitly cover admitted publication and current lookup rather than force current records back into candidate posture. Neither the proposed registry type nor its schema is active.

## Six shared Lab designs

| Gap | Proposed AlchLang boundary | Reuse and remaining work |
| --- | --- | --- |
| L-01: execution context | AssessExecutionContext | Reuse workspace selection and native Project protocol; resolve actual runtime, host, custody, store and effect scope |
| L-02: creation integration | PlanCreationRoute | Route to existing CreateDefinition, CreateRecord, CreateArtifactType and preparation Entries; connect public route to compiled policy and real native writer |
| L-03: semantic compatibility/publication | AssessDefinitionReview, SelectCompatibility, PlanPublication | Review the five meanings, mixed-version registry and exact canonical bundle; implement qualified publisher and consumer adoption |
| L-04: cross-boundary recovery | JoinLifecycle, PlanJoinContinuation | Reuse native proposal/permission/HEAD/outcome mechanisms; persist durable join observations and reconcile original unknown operations |
| L-05: lifecycle and impact | PlanLifecycleImpact | Reuse native revise/withdraw; prove complete declared consumer/dependency closure and publish governed source transition |
| L-06: construction | AssessConstructionEntry, AssessConstructionCompletion | Reuse chain contracts and Craft compilation; implement shared observation gate and independent output-bound conformance |

A Product can be inspected without inventing a Project. An actual effect must use the selected host's supported scope; a project-only native host requires a real Project. Work requires its actual Project, and linked project membership must match. Products remain in one workspace home; runtime execution is a separate selection.

The compiled design includes a proposed Entity and keyed Query for durable join identity plus an inert Proposed-phase initialization transaction. That transaction was not executed. The prototype exercises pure planning selections only; it supplies neither a live journal/store adapter nor active runtime integration.

## Publication and recovery

PUBLICATION-PROTOCOL.json separates three decisions: semantic disposition, native effect permission and canonical publication authorization. Their scopes and exact subjects must match independently.

A native local commit may leave **LocalCommittedAwaitingPublication**. It does not publish the canonical registry. Unknown native outcomes require read-only inspection of the original operation. Unknown publication outcomes require inspecting the selected snapshot and original publication identity. Source changes do not make uncertain effects safe to redispatch.

The proposed publisher prepares a qualified immutable snapshot and changes one current-source selection through an expected-predecessor CAS. It must verify real authorization, native receipt, projections, indexes and consumers. No distributed transaction across the native store and repository is assumed. Ordinary multi-file working-tree edits are not atomic. Legacy direct-path consumers must be migrated or fenced before this model is qualified. Git commit or push alone is not admission.

A changed predecessor or postimage requires new review and appropriately scoped authorization. Preserve existing receipts and unresolved state; never silently re-sign, re-dispatch or declare completion.

## Construction remains shared Lab responsibility

Define owns candidate conversation, capture, Pack preparation, inspection, fidelity/materialization/reconstruction/replay and readiness from verified bindings. It does not select an owner's semantic answer, grant native permissions, publish canonical authority, establish global impact completeness or enforce the full construction chain.

Construction entry needs exact seven-stage/six-adjacent-handoff coverage, current source bindings, real profile/capability closure and executable check specifications. Output manifests and independent conformance results are post-generation completion conditions, avoiding a circular entry requirement.

Existing DomainSpec/prototype-first compatibility obligations remain applicable until explicitly reviewed; choosing AlchLang does not waive them. SOURCE-PROJECTION-SUCCESSORS.json proposes replacements for five retired support references. In particular, semantic owner review cannot be replaced by Define materialization. Reconstruction has only partial current support and still needs the selected real integration adapter.

## Evidence and limits

- Real Craft 1.3.0 / AlchLang 0.7.0-candidate.0 compilation of original authored source; 57 synthetic planning checks pass.
- CONTRACT-VERIFICATION.json reports 220 source/schema/projection checks, including all 189 retained registry-body hashes, the five unchanged candidate bodies, two valid proposed successors and deterministic human projections.
- Positive authority, permission, native outcome and conformance observations in prototype tests are synthetic fixtures. No DTO, flag or hash authenticates itself.
- No production store, native writer, publisher or owner response was exercised. The stateful initialization was not executed. Active runtime qualification and end-to-end integration remain future work.
- Canonical definitions updated: zero. Proposed metadata successors: two. INDEX.json synchronizes proposal navigation only; canonical registry/indexes are unchanged.
- Drift recorded: prior audit carrier/creation claims, two old consumer contexts, five retired source-support references and the difference between the bootstrap registry schema and later admitted publication posture.

Run verify-contracts.py with Python plus jsonschema for artifact checks. Run alchlang/verify-design.mjs with the pinned Node for original-model generation and planning checks. Generated models stay disposable in ignored .local directories; compact results and source bindings are retained.

## Order before implementation

Review the five exact owner requests and optional two successors; review the successor registry contract and explicit compatibility choices; review the six candidate handoffs and inherited construction compatibility; then separately scope implementation of trusted observation ports, route/journal/publication integration and reader adoption. Only real independent end-to-end evidence can qualify activation.

This package is the design for that work, not a claim that the shared gaps have been implemented.
