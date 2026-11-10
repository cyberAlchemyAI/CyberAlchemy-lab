# Definitions and records workflow audit

Date: 2026-11-10. Audited commit: `f045e4e754e9609f3bf226fe3aab04c1d19f7fd8`.

Define now implements the semantic-preparation and portable-candidate workflow. The complete governed definitions-and-records lifecycle remains incomplete. This audit found three confirmed Define content/readiness/correlation defects and one bounded early-authoring validation gap, independently of the larger shared Lab integration and publication work.

No implementation, canonical registry, owner disposition, grant or production store was changed. Test sessions and native writes used isolated temporary fixtures. The shared native source inspection explicitly selected a nonexistent store path, so the operator's default private store was not read.

## Evidence and its limits

- Retained Define evidence: 401 checks across 27 surfaces revalidated for integrity, not all rerun here.
- Fresh Define workflow: 29 checks passed, including Product-only sessions, original-byte materialization, observed package handoff, successor package preparation and fresh-process replay without original packages.
- Fresh shared Lab: 84 fixture checks passed for creation, type registration, signing, local admission, replay, event delivery and interrupted native publication/recovery. These do not qualify an authenticated production adapter or repository publication.
- Additional causal probes found four accepted cases the existing suites do not reject. Their full actual CLI/session/package results are in `DEFINE-BOUNDARY-PROBES.json`; passing regression suites do not close these gaps.
- Canonical registry: 189 admitted versions / 183 current identities; all original digests, Definition/v1 schema checks and colocated human projections passed.
- Source-only native catalog: 444 current subjects, including 183 Definitions and 121 Artifact Types; 806 source files verified. Source replay includes 491 total historical/current subjects.
- Seven Product workspace profiles share one runtime target; zero runtime copies. No native store bindings are selected in the workspace catalog. Product navigation identity does not establish a canonical Product/Project or permission.

## Responsibility boundary

**Define owns semantic preparation:** supplied goal/intent/context/consumer/use, clarification, meaning discovery observations and applicability/dispositions, explicit candidate Definitions/contracts/contributions, local revision, scoped preparation assessments, portable exact-byte packages, handoff and reported acknowledgement. Its session journal is authoritative for this local preparation, not for canonical business/authority records.

**The shared Lab owns governed operations:** workspace/catalog resolution and custody, generic artifact/record/type creation and registered schemas, semantic-owner review routing, actual permission/signing, native transactions and recovery, canonical publication/source transitions, wider lifecycle/dependency impact, and full construction-chain enforcement. Craft owns the selected language/compiler/generation mechanisms; consumer owners assess output conformance.

The full construction chain remains `definitions -> artifacts -> ontology -> business/system bridge ontology -> system ontology -> AlchLang -> generation`, with exact adjacent handoffs and independent conformance. Its executable gate belongs around shared Lab/consumer generation, not inside Define as a universal permission/construction enforcer. The prior audit's suggestion to put that gate in the Define builder is superseded by this ownership boundary.

## Define implementation and remaining work

| Capability | Implemented | Residue |
|---|---|---|
| Context and guided clarification | Product-only preparation without invented Project/Work; Context/Concept questions, actual answered/corrected/deferred/refused states and native next-action guidance | Selected workspace/membership observations remain reported input; authoritative custody is Lab-owned. |
| Discovery/dispositions | Exact catalog lookup, captured matches and empty scope, applicability notes; existing Reuse/Propose/Open/ApplyParameters/ChangeMeaning | Bounded exact lookup, not exhaustive semantic search or automatic suitability/acceptance. |
| Definition authoring | Attributed contribution/draft manifests, missing/ambiguous field counts and real Definition/v2 schema/fidelity/full leaf-lineage materialization | D-04: early field guidance does not resolve source selectors or establish all normative requirements. |
| Revision | Complete Preserve/Recheck/Retire plan, actual predecessor Pack body, preflight, idempotent application and usable successor package | Preserve supports independent Reuse/Propose/Open under unchanged scope. Dependent handling must Recheck; derived applications/assessments/materialization/confirmation clear. |
| Readiness | Actual snapshot/context/count facts, pending-question/unhandled-concept blockers, native materialization proof and scoped typed status | D-01: parameter completion is inferred from application count plus materialization, not actual parameter-binding completion. |
| Handoff/ack | Actual package/request/version/context/consumer bindings, captured members, source-bound journal and replay | D-02/D-03: auxiliary report types/freshness and actual handoff/response correlation are not fully validated. |
| Persistence | Hash chain, atomic publication, source-epoch enforcement, idempotence, unknown-outcome preservation and byte-exact reconstruction | Old source epochs refuse; no general journal migration adapter is implemented. Limits are explicit; no production authorization is inferred. |

### D-01 — Incorrect parameter readiness (P1)

A real package was prepared with one required parameter `E` missing and an explicit `parameter:E` binding gap. Its existing native `pack.json` readiness said **`apply-parameters: blocked`**. A separate valid User Journey Definition in that same package materialized correctly. `assess` nevertheless returned **`Reviewable` for `ApplyDeclaredParameters`** with declared blocker counts zero.

The new mapping computes `parameter_binding_complete = materialization_verified and applications > 0`. An application count and unrelated Definition materialization are not parameter completeness. Reuse the already available application/parameter binding results and use-specific readiness/obligations. This is Define-owned truthfulness, not permission enforcement or a request to move Lab authority into Define. No authority grant or actual parameter execution occurred.

### D-02 — Handoff auxiliaries are only byte-bound (P2)

The actual CLI accepted a matching real package with arbitrary plain text supplied as `preparation_assessment`, `candidate_inventory`, `open_obligations` and `note_manifest`. Actual package/request proof still works; auxiliary types, represented subject, use and freshness are not thereby established. Bind and validate owned report/manifest contracts and declare stale/unknown posture explicitly. Authoritative workspace membership remains with the shared source owner.

### D-03 — Acknowledgement need not reference a handoff (P2)

The actual CLI accepted arbitrary text as both handoff and response when the caller's `response_to` matched that file digest. The result correctly remained `reported-acknowledgement` with no acceptance/permission effect. Still, it does not establish that a PreparedHandoff was acknowledged. Validate the actual handoff shape/identity/cut and allowed correlation. Authenticating a real consumer response is an external host/owner responsibility.

### D-04 — Field assistance counts an unresolved source pointer (P2)

An original JSON document `{"real":1}` was bound, but its contribution specified `source_selector: /missing`. The field checker counted that proposal and returned `missing=[]`, `ambiguous=[]` for the selected `/title` requirement. This is a limit of early guidance; the final full materialization path still verifies leaf sources/fidelity. Resolve source/target selections before calling contributions checked, and distinguish proposed, checked and conflicting contributions. No automatic normative voice/owner synthesis is required.

## Shared Lab implementation and remaining work

| Area | Existing capability | Remaining shared responsibility |
|---|---|---|
| Workspace/catalog | Current source catalog, seven Product profiles, central/specializable runtime model, source-only read/verify | Select real custody, authority/Project/Work and native store/grant bindings for effects. Product-only Define preparation does not supply them. |
| Definition/type/record creation | Native exact-byte/schema/identity/current-carrier validation; compiled CreateDefinition/CreateArtifactType/CreateRecord/PrepareCreation; unsigned drafts and local type registration | Normal `create.py` executes `ports/creation.py` rather than compiled Entries. Select and wire the authoritative path; retain the native writer. This Python is shared Lab code, not the removed Define engine. |
| Review/authorization/commit | Real native exact-HEAD/source/signature checks, atomic transaction/history/consequence generation, deterministic replay and unknown-outcome recovery | The compiled coordinator's selected effect adapter is explicitly `native-fixture`. A real authenticated operator/custody adapter and complete current-workspace qualification remain. |
| Handoff-to-effects | Define emits an exact candidate handoff; Lab can prepare/review/authorize/apply a proposal | Join handoff -> draft -> semantic disposition -> exact proposal/HEAD -> signed approval -> authoritative transaction -> publication receipt, with resumable correlation/recovery. |
| Canonical publication | Native local branch admission and repository governance publication components exist | No joined authorized Definition/v2-compatible registry/index/human-projection/source transition. Registry currently declares Definition/v1; preserve existing admitted historical bytes. Git push/local commit is not canonical semantic admission. |
| Governed lifecycle | Native revise/withdraw and dependency checks already exist | Creation wrappers only prepare Admit/no predecessor. Add lifecycle authoring, dependent type/record/ontology/consumer impact and explicit source/store transitions. Define's local selective revision is not this wider lifecycle. |
| Full construction chain | Five authored candidate Definitions, models, contracts, six handoff contracts, language/profile projection and compiler exist | Generation gate explicitly remains `runtime_gate_implemented:false`; enforce freshness/coverage/capabilities and independent consumer conformance outside Define. Five resource references point to retired Python/connector files and need a reviewed successor mapping. |
| Semantic authority | Owner review packets and contracts exist | Five exact candidate versions still lack canonical admission; no missing authored file or blanket reauthoring is implied. Obtain the applicable exact owner disposition and compatibility selection. |

The five pending owner targets are Lab Workspace v2, Definition Pack, CyberAlchemy Define, Construction Chain Contract and Construction Stage Handoff. Their exact source bytes still match the previous owner-review bindings. A fixture signature or agent assessment does not resolve these admissions.

## Complete stage map

| Stage | Owner | Current status | Detail |
|---|---|---|---|
| CC-01 Workspace/context/intent | Define + shared Lab | Implemented preparation; effects partial | Product-only Define, typed clarification, shared workspace resolution and one runtime. Real effect authority/store mapping remains Lab work. |
| CC-02 Discover meanings/carriers | Define consumes shared Lab catalogs | Implemented bounded discovery | Exact identifier/term matching and bound source observations; no exhaustive semantic search or inferred source authority. |
| CC-03 Capture evidence | Define; generic I/O shared | Implemented | Original bytes, exact bindings, retention bounds and portable self-contained evidence. |
| CC-04 Meaning/contract preparation | Define | Implemented with validation gaps | Questions, dispositions, parameter/application declarations, contribution/draft notes and native policies; D-01 to D-04 remain. |
| CC-05 Definition/v2 materialization | Define; shared type renderer | Implemented candidate path | Full schema/fidelity/leaf-lineage and exact bytes; owner acceptance/publication remains outside Define. |
| CC-06 Definition draft/native proposal | shared Lab | Component implemented; public route hybrid | Native original-byte/schema validation and unsigned drafts; compiled operations and normal CLI are separate. |
| CC-07 Artifact Type registration | shared Lab | Component and fixture-qualified native admission | Explicit schema/contract/meaning closure and native local registration; no automatic new type for every Definition. |
| CC-08 Business/artifact records | shared Lab | Component and fixture-qualified | Explicit current carrier/identity/schema, original bytes and derived-target exclusion; common workspace custody/orchestration incomplete. |
| CC-09 Semantic-owner review | shared Lab/actual semantic owner | Governance partial | Review/assessment contracts exist; five exact owner targets remain unadmitted. Structural validation is not semantic disposition. |
| CC-10 Exact authorization | shared Lab native owner | Implemented; non-fixture deployment not qualified | Real native Ed25519/source/HEAD checks in isolated tests; no default grants or operator-store onboarding inferred. |
| CC-11 Commit/replay/history | shared Lab native owner | Implemented local branch | Atomic HEAD, transactions, histories/consequences and replay; does not update repository canonical registry. |
| CC-12 Unknown outcome recovery | each component; shared coordinator for joins | Components implemented; join incomplete | Define journal and native local transaction recovery work; cross-package/review/publication resume is not joined. |
| CC-13 Retained reconstruction | Define; shared discovery/catalog | Implemented portable Define path | Byte-exact package reconstruction and replay after original package removal; wider committed-work discovery is separate. |
| CC-14 Revision/withdrawal/impact | Define local meaning; shared Lab governed lifecycle | Partial | Define selective carry/recheck/retire works within declared limits. Native revise/withdraw exists; generic creation wrappers are Admit-only. |
| CC-15 Canonical publication | shared Lab governance | Not joined | Explicit compatible Definition/v1-v2 canonical registry/index/projection/source transition remains missing. |
| CC-16 Full construction/generation chain | shared Lab coordinator + Craft/consumer owners | Contract only | Definitions -> artifacts -> ontology -> business/system bridge -> system ontology -> AlchLang -> generation requires an external executable gate and conformance assessment. |

## Recommended build order

1. Tighten the Define-owned use-specific readiness and report/handoff/acknowledgement contracts first; add these causal probes to its persistent regression suite. Improve selector validation without expanding Define into Lab governance.
2. In parallel, resolve the five existing owner/compatibility decisions and prepare current source/design projection successors. Do not rewrite old frozen approvals until their old hashes appear to authorize new behavior.
3. Wire the actual shared creation operations and a selected non-fixture authority/custody host, using the existing native writer and one runtime.
4. Build the persistent cross-boundary coordinator and canonical v1/v2-compatible publication/source transition, then lifecycle/impact paths.
5. Execute the shared construction-chain gate and qualify one real selected-workspace journey plus denial, stale input, interrupted/unknown commit and replay cases. Keep local, fixture and canonical outcomes separate.

Implementation fixes were not performed in this audit. Exact evidence and source line/digest anchors are in `SOURCE-EVIDENCE.json`, `DEFINE-BOUNDARY-PROBES.json`, `REGISTRY-AND-CATALOG.json`, `GOVERNANCE-AND-CHAIN.json`, `TEST-RUNS.json` and `RESULT.json`.
