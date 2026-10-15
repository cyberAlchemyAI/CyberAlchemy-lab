# Review handoff contract

Contract owner: Lab host successor. Design status: specified; implementation and qualification pending. This closes the missing ordering, input custody and authorization-selection design. It does not assert permission for a real review today.

## 1. Observed constraints

The selected API17 reference:

- validates an exact immutable workspace input set and policy-bound manifest (`workspace.py:34–53`);
- requires preselected metadata and already supplied decision-core bytes (`candidate.py:38–40,61–68`);
- compares host-recomputed cores with those supplied bytes (`candidate.py:90–94`);
- namespaces generated object refs by workspace identity (`workspace.py:103–109`);
- selects review routing lazily, but only from a selected Vault input (`service.py:138–147`);
- checks a hardcoded historical authorization in both authentication and review routing (`auth.py:239–244`, `review_preparation.py:31–34`).

The successor must preserve exactness and replace the historical-policy special case with the explicit current scoped policy below. New candidate bytes cannot be injected into an active Vault; `package.import` is not the route because its present implementation restricts source roots to Work candidates.

## 2. Inputs and outputs

These are closed local implementation contracts, not new Lab Artifact Types.

### `ReviewCohort`

Required fields: `schema_version`, `cohort_id`, `revision`, `source_cut`, `source_profile_binding`, `native_mechanics_bindings`, `scope_ref`, `ordered_targets`, `schema_bindings`, `evidence_bindings`, `owner_route_selections`, `examples_binding`, `consequences_recipe_binding`, `privacy_review_binding`, `authority_effect:none`.

Each ordered target contains exact proposed identity/version/carrier/category/operation, original candidate bytes binding and size (null for withdrawal), exact predecessor where required, selected contract binding, proposed Decision identity, requested effect and complete dependency selectors. Relation additions require their own exact typed targets and declared endpoint pairs. Owner-route selections identify actual selected profile/preference/principal/role-declaration sources or explicit blockers. They do not appoint owners.

The closed target entry fields are `target_id`, `category`, `operation`, `artifact_header`, `predecessor_ref`, `content_binding`, `candidate_contract_binding`, `decision_ref`, `native_contract`, `requested_effect`, `dependency_refs`. `artifact_header` is the selected native exact header shape, not an invented semantic digest; byte-free withdrawal uses the exact current predecessor header. Bindings, evidence and owner-route objects use their selected closed native schemas. Additional fields or unrecognized union branches refuse.

`C = raw SHA-256(canonical Python encoding of ReviewCohort)`. Canonical encoding is the new-record contract in [CONTRACTS](CONTRACTS.md); C is not a host target digest. No grant, workspace hash, future signature, generated proposal-object locator or later owner outcome is inside C. The ordered cohort cannot be silently truncated or partially applied.

### Scoped operator policy and selection

The independently installed selection binds:

- exact host/extension/schema/native-authority-verifier implementations and public-key algorithm;
- actual operator principal/key binding and actual authority-basis refs from the selected current Lab scope;
- permitted source/profile/scope, operation subset and exact cohort C;
- independently owned output parent and expected directory identity, plus byte/target/action ceilings;
- absolute not-before/expiry, current revocation selection and purpose `candidate-review-preparation`;
- independently scoped issuer selection, signature/proof bindings and `authority_effect:none` on resulting candidate material.

The policy permits staging/validation/review preparation only. It cannot permit semantic admission, governing application, owner signing or new RoleAssignments. A retained-material permission is separate, even if one principal holds both.

**Permission decision:** the host validates its external installation selection and invokes its selected native authority verifier on the actual current issuer/principal/key/assignment/Policy scope. It verifies the exact policy bytes/signature and source/caller/operation/cohort bindings, verifies the fresh nonce proof for this channel, checks current revocation and real time, then intersects all limits and periods. Every check must succeed. An unavailable verifier, candidate-only basis, unbound key or historical fixture authorization returns `authority-unavailable`; no fixture issuer or locally generated key substitutes for it. Actual values are required deployment inputs, not manufactured by this design.

### `StageReviewRequest`

Required fields: `request_id`, `idempotency_key`, `cohort_binding`, `operator_selection_binding`, `target_input_bindings`, `requested_deadline`, `limits`, `authority_effect:none`. Inputs are exact original buffers or independently permitted descriptors; no arbitrary runtime imports or code from the request execute. Core/metadata construction is host-owned, so the client does not have to mint a trustworthy core.

### `StageReviewResult`

On success: exact request/C/source bindings, `workspace_ref`, workspace manifest binding, separately located policy selection binding, ordered target metadata/core bindings, routing binding, complete target headers and a stage receipt. It states `candidate-only`, `actual_owner_outcome:null`, `current_owner_authority_verified:false`, and `authority_effect:none` for the candidate result. Stage success proves selected input publication only, not the later host validation or owner outcome.

The result's closed fields are `schema_version`, `request_binding`, `cohort_binding`, `source_cut`, `workspace_ref`, `workspace_binding`, `policy_selection_binding`, `target_bindings`, `routing_binding`, `stage_receipt_binding`, `posture`, `actual_owner_outcome`, `current_owner_authority_verified`, `authority_effect`. A refusal uses the ordinary result/diagnostic envelope, never a success object with unresolved required bindings.

On refusal: code, affected target/input/use, no falsely ready selection, and any owned staging/operation inspection binding permitted for the caller. Private policy/key/body data is not emitted in errors.

## 3. Exact native core construction

The stager uses the selected host's own pure helpers after checking their exact import/source closure. It does not independently translate host encoding into Node or replace a native validator. For every target, in order:

1. Capture/hash/strictly parse the same original candidate buffer; check its identity, carrier/schema and scope. Read exact selected predecessors for successor/withdrawal; do not resolve a mutable alias later.
2. Build selected metadata `{schema_version, category, decision_ref, contract}` under the existing target-metadata semantics.
3. Build the native runtime target with exactly `category`, `operation`, `version_ref`, `carrier_ref`, `record`, `predecessor_ref`, `decision_ref`, `contract`.
4. Under the selected custody representation, add `content = native.custody.content_entry(original_bytes)`, or null for withdrawal, exactly as the reference kernel does. Keep noncustody and custody target representations distinct.
5. Set `core = {decision_ref, category, operation, version_ref, target_digest:native.common.digest(runtime_target)}`.
6. Set `core_bytes = native.common.encoded(core)`. Bind those **file bytes** with raw SHA-256. The host target digest uses compact canonical JSON in the inspected reference; `encoded` uses sorted indented JSON plus LF. These are different digest/byte domains, and the selected host helper governs both.
7. Reject unsupported category/carrier/representation or unresolvable dependency. A prospective new carrier must be represented by its selected compatible native contract and complete cohort; it cannot borrow an unrelated current carrier.

The exact-schema/original-content native preparation path then independently validates the complete prospective set. Target core inputs must remain equal before/after any custody/schema wrapper, matching the reference kernel's comparison. The stager's calculations are proposed control material, never owner signatures.

## 4. Ordered staging and submission

```mermaid
sequenceDiagram
  participant D as Define
  participant S as Host stager
  participant V as New immutable workspace
  participant H as Host validator / review
  D->>S: Exact cohort C and independently selected permission
  S->>S: Verify authority, cut, bytes, metadata and native core recipe
  S->>V: Stage exact inputs, routing and workspace manifest
  S->>S: Recheck source, permission, limits; publish new selection
  S-->>D: Exact workspace / policy / core pins
  D->>H: Authenticate actual new host channel
  D->>H: change.prepare / change.validate for exact cohort
  H->>H: Recompute targets, cores and prospective closure
  D->>H: proposal.review using this workspace's returned evidence
  H->>H: Independently revalidate complete original proposal
  H-->>D: Pending exact final review, no owner outcome
```

Detailed order:

1. Freeze C and exact target bytes. If Source/Work retention targets are selected, obtain the real retained-root completion receipt first and include its binding in cohort evidence.
2. Under the permitted operator selection, allocate a fresh workspace identity and fresh output location. Build metadata/cores with the recipe above. Derive independently selected required owner voices/profile/preference routing against this exact C, core order and source cut. Incomplete standing or scope blocks review eligibility.
3. Construct a new workspace input set containing all bodies, selected schemas/evidence, target metadata, core bytes and review routing. Flatten input filenames under the existing workspace grammar; retain the ref→digest map. Use no symlinks, foreign files or invented `workspace-object` inputs.
4. Construct the immutable workspace manifest. Routing binds the separate current scoped authorization basis, source cut and ordered cores, not the manifest or a future approval. A successor routing/schema branch explicitly replaces the historical basis and protocol-prefix special case; no in-place change to API17 occurs.
5. Write a separately stored channel policy that binds this actual manifest hash, principal/public key, allowed preparation operations and bounded period. Its expiry is no later than every applicable source/assignment/operator-policy bound. Metadata-only contexts retain null machine Session/assignment refs. Never supply an agent identity merely because Define was invoked by an agent.
6. Validate the staged closed file set, modes/owners, exact byte sizes/digests and dependencies. Recheck source head and permission immediately before committing the new selection. Flush files/directories; publish the owned staging root by supported atomic no-replace semantics. The readiness receipt lives in the owned **outer** operation root, not as an unselected child of the Vault.
7. Start/select the exact successor host with the new workspace/policy pins. Authenticate through its actual fresh nonce protocol. Recheck current source/profile/cut, scopes, expiry and required operations before submitting. Staging alone did not authenticate this new host channel.
8. Build the change envelope using the actual trusted actor/context and new `workspace_binding`. Call existing preparation/validation operations as required by the selected protocol. Use only their actual returned validation/example/consequence/privacy/core/proposal bindings.
9. Submit `proposal.review` in this same workspace namespace. The host recomputes the complete original proposal and compares exact results and ordered routing. Record the pending review/checkpoint and evidence. Actual owner decisions remain absent.

A new workspace may retain the same source cut; compare rather than assume either change or stability. Generated proposal/review object refs from an earlier workspace are never transplanted. New input, source, scope, schema, core order or selection changes require restaging and affected revalidation. Partial user selection creates a new cohort.

## 5. Atomicity, idempotency and recovery

The host local operation journal is outside disposable review roots and excludes machine short memory/private keys. Its key is `(host selection, principal, scope, operation, idempotency key)`; its fingerprint binds exact C, policy selection and output scope, not a fresh nonce or caller-supplied authority context.

| Observation | Behavior |
| --- | --- |
| Same key/fingerprint and complete staged result | Recheck current permission and return original exact selection; do not rewrite it |
| Same key with different cohort/output/policy input | Conflict; require explicit new request |
| Crash before selection commit | Return incomplete/owned residue through local inspection; do not start the host |
| Crash after selection commit, before reply | Inspect journal plus exact filesystem selection; return original result only after verification |
| Native `change.prepare` or review outcome unknown | Use that branch's actual `operation.inspect`; do not reissue with a fresh key to force a second effect |
| Expired/revoked permission or changed source | Refuse further use; retain history, obtain a separately valid request and restage/revalidate as required |
| Bytes or selected root identity change | Integrity failure; no digest refresh or overwrite |

Local staging inspection and native branch inspection are distinct. A local receipt cannot answer whether an actual governing operation committed. Cleanup may remove only identified owned temporary staging under its declared policy; it never deletes retained roots, old workspaces or unknown residue automatically.

Inspection after an old permission expires requires a fresh separately scoped read/recovery permission for the exact old operation/workspace. It never extends the old grant or permits a new effect. The host branch owns verification of its native journal/epoch through its qualified inspection/recovery route. If a changed source/profile makes that route unavailable, the result remains explicitly unknown pending native recovery; Define must not manufacture a replacement success inspector.

## 6. Preconditions at actual application

Actual native Governance/owner ingress checks the selected exact cohort, actual independent owner voices/outcomes, current principal/key/role scope, standing/profile/representation prerequisites, expected head and complete generated consequences. The same principal may fill different roles only through their separately verified obligations. A candidate `current_owner_authority_verified:false` record cannot satisfy this boundary.

The existing single final checkpoint remains all-or-nothing. A selected rejection, missing outcome, changed member or blocked compatibility condition cannot be treated as an accepted complete cohort. Host publication/recovery remains governed by the existing native epoch contract.

## 7. Design closure and later evidence

The ordering/custody gap is closed by this specified stager, exact core recipe and current scoped policy branch. A real deployment must still provide actual issuer/principal/key/scope/period selections and implement/qualify the successor. Acceptance cases H01–H09 in [REVIEW](REVIEW.md) must demonstrate it before a working handoff is claimed.
