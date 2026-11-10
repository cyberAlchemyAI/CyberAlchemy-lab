# Definitions and records workflow: post-validation audit

Audited commit: `cf77d5580063f664e196b8c338123879bb6f11a9`. Date: 2026-11-10. Overall outcome: **GAPS REMAIN**.

Define's handoff, acknowledgement and selector corrections hold in the current regression suite. Parameter readiness is only partially fixed: the original unrelated-materialization case is rejected, but a stronger self-consistent modified-package case still produces false Reviewable readiness. The complete governed definitions/records workflow also remains incomplete across the shared Lab boundary.

No implementation, registry, permission, owner disposition or production store was changed. Test writes use isolated temporary fixtures. Source catalog commands explicitly selected an absent store, so the operator's private store was not inspected. The fixture driver's generated receipt was retained here and restored at its tracked location.

## Current verification

- 441 retained Define checks revalidated for source/evidence integrity; all 441 were not rerun in this audit.
- 38 persistent Define validation checks freshly passed, covering the earlier four causal cases and positive controls.
- 84 shared Lab fixture checks freshly passed on an isolated retry. The initial parallel run timed out in `artifact-type-checks` after creation checks passed; its log is retained. It is not counted as a pass.
- One additional adversarial readiness probe was **accepted incorrectly** and survived independent-process replay. Passing suites therefore do not establish readiness closure.
- Registry: 189 admitted versions / 183 current Definition identities, with all original digests, Definition/v1 schemas and human projections checked. Source catalog: 444 current subjects, 806 verified source files, 491 replayed historical/current subjects.
- Seven Product workspace profiles, one shared runtime target, zero runtime copies. Native effect store bindings are not selected.

## Define-owned implementation

| Capability | Implemented | Boundary or remaining work |
|---|---|---|
| Context and clarification | Product-only preparation with optional Project/Work; actual Context/Concept questions, responses/refusals/defer states and native next-action guidance. | Workspace membership/custody is a reported external observation, not Define-created authority. |
| Meaning discovery and dispositions | Bound exact identifier/term lookup, captured matches/empty scope, applicability observations; Reuse/Propose/Open/ApplyParameters/ChangeMeaning. | Bounded discovery and declared applicability; no exhaustive search or semantic owner acceptance. |
| Definition and contract preparation | Attributed contributions/drafts, actual source/draft pointer resolution, native distinct-value conflict checks. | Selected field assistance does not establish every normative requirement. |
| Definition/v2 candidate output | Actual schema, fidelity and complete leaf-lineage checks; original-byte materialization and portable packages. | Canonical carrier compatibility, semantic admission and publication remain shared Lab/owner work. |
| Scoped readiness | Actual session facts, blockers, current package/request binding, requested-use selection and real candidate materialization checks. | **D-05 open:** readiness declaration in a self-consistent package is not independently derived from actual parameter facts. |
| Revision | Exact predecessor Pack, complete Preserve/Recheck/Retire coverage, native preflight, idempotent successor preparation. | Independent Reuse/Propose/Open may Preserve with unchanged scope; dependent handling requires Recheck and derived state clears. |
| Handoff and response | Typed subject-bound inventory/evidence/obligation/assessment reports; read-only `handoff-input`; actual prior producer handoff, typed correlated response and captured producer bytes. | Reported receipt is not authenticated consumer acceptance. |
| Persistence and recovery | Hash-chained canonical journal, atomic publication, exact source epochs, idempotence, unknown-outcome preservation and portable replay/reconstruction. | General cross-epoch journal migration/reopening is not implemented; unsupported epochs refuse rather than silently rebase. |

### D-05 / D-01 remainder: readiness declaration versus derivation

The original actual package contains required parameter gap `parameter:E` and says `apply-parameters: blocked`. In an isolated copy, the audit changed only that readiness outcome to `ready` and updated the package body's manifest digest/length. The application, request and missing E value were unchanged.

`inspectPackage` returned `frozen_integrity: verified`. `assess ApplyDeclaredParameters` then returned **Reviewable**, and a separate process accepted replay. No permission or domain execution occurred; this is a false preparation claim.

The source path is concrete: `runtime/package.mjs` exposes the body's readiness map; `preparation/validation.mjs` selects that map entry as `native_use`; `EffectivePreparationCheck` treats Ready plus a nonzero application count as complete. Frozen byte integrity is not proof that readiness was computed correctly. New handoff report equality checks do not independently establish the truth of that underlying observation.

The next Define fix should reuse the existing AlchLang application/binding/readiness policies over verified retained facts, compare or replace the package's declared result, and retain the independent derivation. Add this exact modified-package witness to persistent regressions, alongside complete, incomplete and unobserved controls. This requires neither Lab permission enforcement nor a universal construction gate in Define.

Exact result: `READINESS-CLAIM-PROBE.json`. Source/digest/line anchors: `SOURCE-EVIDENCE.json`.

## Shared Lab implementation and gaps

| Area | Implemented | Still required |
|---|---|---|
| Workspace and authority context | Seven profiles, central/specializable runtime selection, verified source catalog and native Project branches. | Bind actual custody, native stores and grants; select a real host. Public creation is Project/Work scoped; Product-only Define preparation does not manufacture an authorized effect context. |
| Definition/type/record creation | Compiled CreateDefinition/CreateArtifactType/CreateRecord/PrepareCreation, native byte/schema/identity/carrier validation, unsigned drafts and type registration. | The public `create.py` route still calls Python `ports/creation.py`; connect the selected authoritative creation route to compiled Entries and the existing native writer. This Python belongs to shared Lab, not the removed Define engine. |
| Authorization and native commit | Actual source/HEAD/Ed25519 checks, atomic local transactions, history/consequences, replay, event delivery and unknown-outcome recovery. | The compiled effect adapter is explicitly `native-fixture`; selected real custody/operator integration and production qualification remain. Native implementation exists and should be reused. |
| Handoff-to-publication join | Define exact candidate handoff and Lab draft/review/authorize/apply components. | Persistent correlation through semantic disposition, exact proposal/HEAD, signed approval, transaction and canonical publication receipt; resume uncertain outcomes across those boundaries. |
| Canonical compatibility/publication | Registry Definition/v1 and native local branch admission; Define candidate Definition/v2. | An explicit compatible carrier/schema and registry/index/human-projection/source transition. Native local admission and Git push do not perform canonical semantic publication. |
| Governed lifecycle | Native revise/withdraw/dependency checks and local Define revision. | Lifecycle authoring beyond Admit-only creation wrappers, dependent type/record/ontology/consumer impact, and explicit source/store transitions. |
| Full construction chain | Authored definitions/models, all six adjacent handoff contracts, language/profile selection and Craft compiler. | Gate is explicitly unimplemented; five resource intentions reference retired files. Reviewed successor mapping, executable freshness/coverage/capability gates and independent consumer conformance remain outside Define. |

Five **existing exact candidate versions**, not five missing authored files, still lack canonical admission: Lab Workspace v2, Definition Pack, CyberAlchemy Define, Construction Chain Contract and Construction Stage Handoff. Their bytes still match the prior owner-review bindings. Exact owner disposition and compatibility selection cannot be replaced by a fixture signature or a rewritten old approval hash.

The construction chain remains:

`definitions -> artifacts -> ontology -> business/system bridge ontology -> system ontology -> AlchLang -> generation`

Define prepares meanings/contracts and candidate evidence. The shared Lab owns authoritative artifact/record creation, custody, permission, admission, publication and cross-boundary enforcement. Craft owns the selected language/compiler/generation mechanisms; consumer owners assess conformance. There is no reason to put those shared responsibilities into Define.

## Next work in dependency order

1. Close D-05 using the existing Define AlchLang chain and persistent causal regression; keep authority outside Define.
2. Resolve the five exact semantic-owner/compatibility selections and reviewed current source projection successors.
3. Connect shared creation Entries and actual workspace/custody/grant/host selections to the existing native writer.
4. Join handoff, review, authorization, commit, publication and recovery, then expose governed lifecycle/impact paths.
5. Execute the shared construction-chain gate and qualify one real selected-workspace journey, including denial, stale input, interruption and replay cases.

The complete 16-stage map is in `COVERAGE.json`; current findings and ownership are in `FINDINGS.json`; exact registry/governance and fresh test evidence are colocated. This audit does not implement the remaining work.
