# Design review, closure and delivery gates

Scope: author source/contract consistency review before implementation. The review uses source inspection, dependency/cycle reasoning, worked examples and document integrity checks. It is not independent owner approval, executable testing or operational qualification.

## 1. Eight Distill findings applied

| Finding | Revised design action | Design disposition |
| --- | --- | --- |
| D01 component anatomy | Three behavioral responsibilities; no mandatory dozen-module rewrite; compatible reuse is evaluated under C06 | Closed |
| D02 generalized adapter | One concrete exact local installation selection; snapshot bundle is historical input, not a fallback live backend | Closed |
| D03 review input custody | Host-owned stager, preexisting exact core recipe, current scoped policy branch and immutable new workspace sequence | Closed by specified successor contract; implementation pending |
| D04 mixed epochs | Three input populations; exact membership comparison; supplements never inherit host standing | Closed |
| D05 later readiness | Separate use observation; changed input/use/payload/concepts/meaning follows new frozen revision rule | Closed |
| D06 root without closure | Manifest-root identity, complete required member store, digest-bound receipt, carrier resolver and cold-read algorithm | Closed by specified successor contract; implementation pending |
| D07 authoring/parameters | Attributable interaction mapping and exact clause-bound parameters; unsupported assistance/declarations remain visible | Closed as behavior; per-input evidence still required |
| D08 delivery objective | Snapshot core step retained; first live-integration acceptance exercises actual host capture/refusal/cleanup | Closed |

“Closed” means the missing design responsibility/order/contract is now specified. It does not mean future code, policy issuance or proof obligations have been completed.

## 2. Self-review corrections incorporated

- Core construction is a host-stager responsibility before `change.prepare`; host validation recomputes it independently. Compact target digest and indented core-file bytes are explicitly different domains.
- Routing is preselected input despite lazy lookup. A new workspace regenerates object refs/envelopes; its source cut is compared, not assumed changed.
- Both authentication's historical metadata authorization and review routing's historical authorization require the explicit successor policy branch. Changing routing alone would leave authentication refusing.
- API17 metadata contexts have null machine Session/assignment refs. Candidate review does not fabricate machine identity or combine Base/Action/Governance permissions.
- Source/Work publication follows a real retained completion receipt. Future Source/owner/review bodies remain outside R, eliminating a containing-hash cycle.
- Required members use a single indexed manifest map. A rooted URI cannot turn a caller path or second decoding interpretation into storage authority.
- Receipt digest is pinned by Source provenance, not trusted merely because a file named `complete.json` exists.
- Store scope, read/write permission and retained byte lifetime are separate. First implementation is one Lab scope per store; cross-scope copying is unsupported.
- A partial/streamed member result cannot become a complete reconstruction. Full required closure verifies before a complete result/local output is published.
- Retained data cannot include Session short memory or private credentials. Prohibiting a required member blocks retention rather than silently changing bytes or weakening the required set.
- Existing carrier fields and typed relation endpoint rules remain authoritative. New locator/reference interpretation is a versioned implementation resolver, not implicit ontology admission.

## 3. Hash/dependency order

```text
exact input/meaning/evidence buffers
        ↓
frozen Pack P and report/capture/lineage members
        ↓
root manifest R + retained members → real completion receipt D
        ↓
optional Source(R,D), Evidence Set and Work target bodies
        ↓
selected materialized Definitions + optional retention targets → cohort C
        ↓
host target metadata and exact native core bytes
        ↓
current scoped routing → new workspace manifest → selected channel policy
        ↓
actual authenticated change/review evidence → actual owner outcomes
        ↓
native governing epoch / observed consequences → later read observation
```

No receipt hashes itself; C excludes its later policy/workspace/owner outcomes; R excludes future records that reference R. Signing adds an outer binding to already frozen bytes. Host operations still independently check source/head/permission at their actual boundary.

## 4. Delivery slices

| Slice | User-visible evidence required later | Distinct permission/effect boundary |
| --- | --- | --- |
| Core preparation step | Fixture/snapshot inputs → exact conforming Pack/report or truthful gaps; all dispositions, parameters, evidence import and revision behavior | Local candidate preparation only |
| First live integration acceptance | Actual selected permitted host/context capture → Pack; stale/expired/missing-operation refusal; owned Session cleanup; original legacy behavior preserved | Actual Base context/source permission and selected provider |
| Review handoff | Complete Definition selection → actual staged new workspace with exact cores → independent host validation/review; stale/changed/unauthorized cases refuse | Scoped operator staging/review permission, applicable profile/carrier/owner-route standing |
| Durable result and reconstruction | Actual retained full closure → separately authorized Source/Work publication → fresh process/Session exact reconstruction | Retention permission, native owner/application effects, fresh read permission |
| Realization/adoption | Exact final implementation/source/dependencies/docs, qualified bounded use, independent Product/Capability adoption and launcher selection | Existing actual owners and release/adoption route |

Core implementation can progress before operational prerequisites exist. Missing live permission or host qualification does not turn snapshot evidence into live evidence. Staging and retained storage can be built as bounded host successor work, but the actual effect routes remain disabled until their independent requirements are met.

The original 79 task identities are retained in [work-crosswalk.json](work-crosswalk.json). This design is not a new completed work ledger or a detailed execution work-pack. A later implementation plan can split host work beneath the mapped owners without silently closing earlier tasks.

## 5. Future acceptance matrix — not executed

These cases are specifications for later qualification, not tests added or run in this design task.

| ID | Required case and oracle |
| --- | --- |
| P01 | Original byte capture equals bytes hashed/decoded; duplicate keys, unsupported precision, swapped buffers and malformed UTF-8 refuse |
| P02 | Exactly one disposition per concept; application preserves meaning; undeclared tolerance/parameters reject; incomplete bindings remain explicit |
| P03 | E1 host + E2 local candidate cannot inherit E1 standing; copied claimed member must match exact host binding |
| P04 | Imported synthetic assessment keeps producer/execution limits; bare counts cannot establish a completed Evaluation |
| P05 | Later observation leaves P unchanged; changed intended use/input/payload/meaning requires a new frozen revision with lineage |
| P06 | All legacy command protocols/numeric behavior remain under v1; new Pack compile refuses before effects |
| P07 | Live integration uses actual selected host/session/context, refuses expiry/stale source and closes owned resources; fixtures cannot satisfy this oracle |
| H01 | Fresh selected body/metadata/core/routing resolve in a new immutable workspace; active Vault remains unchanged |
| H02 | Proposed core bytes equal the actual selected native encoding/recomputed core, including custody content; compact target hash is not core-file hash |
| H03 | Wrong principal/key/scope/operation/cohort/policy/issuer/expiry/revocation refuses before stage commit; historical fixture basis cannot authorize this path |
| H04 | Both successor authentication and review use the same actually verified scoped basis; no hardcoded historical substitution remains |
| H05 | Old workspace-object locators reject in new workspace; fresh proposal/review evidence binds new W and exact current source cut |
| H06 | Independent `change.prepare`/review recomputation matches exact complete cohort, schemas/cores/evidence/privacy/consequences and ordered voices |
| H07 | Changed source/schema/selection/owner-route or partial target selection invalidates affected preparation/review and requires a new cohort |
| H08 | Interrupted stage before/after commit is inspectable; same idempotent request returns original exact selection, conflicting fingerprint refuses |
| H09 | Candidate pending review has no owner outcome; actual governing application requires independent real outcomes under the native final-checkpoint rules |
| R01 | Real retained root plus full required member graph is committed; root alone, absent members or graph ambiguity cannot complete |
| R02 | Source content digest binds R and provenance pins exact receipt D; modified receipt/store/root identity refuses |
| R03 | A fresh process/Session resolves exact Work→Source/Evidence→R→P and verifies every required member/selector, preserving original FAIL/open/candidate posture |
| R04 | Expired/revoked read permission refuses despite retained bytes; fresh permission does not mutate P or restore Session RAM |
| R05 | Missing/corrupt/unauthorized required evidence returns exact reconstruction gaps, never an optional downgrade or regenerated replacement |
| R06 | Unsafe paths, symlinks, duplicated IDs, unsupported encodings, noncanonical locator forms, excessive budgets and existing output destination refuse |
| R07 | Byte custody completes before Source/Work application; rejection leaves unlinked material; no admitted dangling new result is accepted |
| R08 | Lost native commit response is reconciled through actual branch inspection/epoch receipt; no automatic new-key redispatch |
| R09 | Existing Source/Evidence Set/Work schemas and exact typed reference/endpoint constraints hold; candidate refs cannot become current admission by resolution |
| R10 | No private credentials/Session short memory enter retained closure; privacy checks do not silently reserialize governing/source bytes |

Original verification obligations remain in force through their existing source references. This matrix adds explicit oracles for the distilled gaps; it does not replace broader semantic, compatibility or realization qualification.

## 6. Remaining deployment inputs and effects

These are required runtime inputs/evidence, not unresolved design alternatives:

1. Exact implemented host/Define successor and complete source/profile/schema/dependency selections.
2. Actual current native authority verifier, issuer/operator/principal/key binding, allowed scope/operations, separate retention/read grants and bounded periods.
3. Actual compatible source/provider/carrier/profile standing and any representation/consumer amendments required by the selected targets.
4. Independently owned store identity/root and local filesystem/transfer guarantees within this contract.
5. Actual evidence/parameters/handling required for each real input; fresh domain Method evidence if an assessment execution claim is made.
6. Actual owner outcomes, native publication/recovery evidence, read-back and separate realization/adoption decisions.

No actual values or effects are invented to make the design appear operationally ready. The next step after review is a bounded implementation plan for these exact contracts, not runtime deployment or admission.

## 7. Authoring method and claim ceiling

Applied the accepted Distill reduction using the existing repository design package as the unambiguous local recipe. The installed Invoke root skill was read, but its referenced `design.md` mode contract was absent from the installed package and searched canonical locations. Therefore no complete Invoke mode validation is claimed; the root's six-view/provenance/handoff conventions guided the repository-native design.

ARE route lookup found no matching route; context/effect/continuation receipts grant no authority. No Arcanum adapter/evolution dispatch occurred. Direct user-authorized local design authoring only.

See [validation.json](validation.json) for exact source/previous-package/coverage/navigation checks. They establish document integrity and explicit design coverage only. They do not prove software correctness, arbitrary semantic consistency, cold reconstruction, real issuer authority or any applied effect.
