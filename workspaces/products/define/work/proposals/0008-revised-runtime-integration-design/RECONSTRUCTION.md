# Retention and reconstruction contract

Contract owner: Lab host successor. Design status: specified; implementation and cold-read qualification pending. This closes root identity, required-member resolution, lifetime and Project State linkage at the design level.

## 1. Selected mechanism and ownership

Use a persistent host-owned local content-addressed material root, selected by exact store identity, owned directory identity and an external current custody policy. The first implementation selects exactly one Lab scope per store; cross-scope copying requires a separate authorized route and is unsupported here. It is outside Git, review `/tmp` roots and private-key custody. It contains only explicitly permitted retained result bytes and control receipts; it is not a new governing ledger or hidden agent memory.

The current API17 workspace is temporary, and its `workspace-object` refs are workspace-specific. Its package exporter also publishes under the temporary workspace; import supports only a restricted candidate Work path. Neither is declared a permanent Pack resolver. The new host extension is the required selected route for this design.

Proposed physical layout:

```text
<independently-selected-retained-root>/
  objects/sha256/<first-two-hex>/<64-hex-digest>   exact original buffers
  packages/<root-digest>/complete.json            immutable completion receipt
  journal/<operation-id>/...                     bounded custody operation records
```

The selected root/store configuration lives separately and contains no client-supplied path authority. Private keys and Session memory are excluded. There is no mutable “latest Pack” pointer in this store; governing selection is the Lab's existing Project State.

The closed store selection has `schema_version`, `store_id`, `scope_ref`, `root_locator`, `root_identity`, `host_extension_binding`, `filesystem_contract_binding`, `custody_policy_binding`, `read_policy_binding`, `limits`, `authority_effect:none`. The independently owned/pinned root selection is verified before use and at commit/return. These actual locators/identities are deployment inputs; no path shown here is an initialized store.

## 2. Root identity and manifest

Use `cal.define.package-manifest/v1` as a local package format, not an Artifact Type. Required fields:

| Field | Contract |
| --- | --- |
| `schema_version`, `package_id`, `revision` | Exact format and frozen work package identity |
| `pack_binding` | Member ID, raw SHA-256, size and media type of exact `pack.json` |
| `members` | Map keyed by member ID; each closed entry has safe logical relative path, role, encoding/media type, raw SHA-256, size, required flag and dependency member IDs |
| `required_roots` | Explicit complete roots for reconstruction, including Pack, capture, report/lineage and required evidence |
| `closure_purpose`, `limitations` | `frozen-pack-inspection`; exact evidence/standing limitations preserved |
| `authority_effect` | `none` |

Member IDs and logical paths are unique, canonical and bounded. No absolute paths, traversal, symlinks, platform aliases or duplicate IDs. Logical paths map to hash-addressed objects; the resolver never follows arbitrary locators supplied inside a member. Validate every dependency ID and traverse with a bounded visited set. A finite reference cycle between already frozen members is not a containing-hash cycle and must not cause infinite traversal. Internal Pack selectors resolve inside an already verified member and do not create recursive downloads.

Serialize the new manifest once under the Python canonical new-record contract. Let **R = raw SHA-256(exact manifest bytes)**. R names the package; it is distinct from the Pack-file digest, canonical-entry digests and host target/core digests. The manifest excludes itself; Pack/member bytes contain no containing-manifest digest. Required reachability includes all roots and recursively required dependencies; optionality cannot override a required dependency edge.

The required set includes exact captured content needed for the claimed frozen inspection, original meaning/evidence buffers selected for that claim, and selector/entry verification. Permitted Context/Ontology Views may be retained; private Session short memory and credentials may not. Remote evidence is fetched only if separately permitted and then captured before freezing. Unsupported or forbidden required material blocks complete retention. Do not mark it optional merely to obtain a successful receipt. A Pack may already contain honest evidence gaps; reconstruction preserves those gaps rather than promising an assessment the Pack never established.

Reconstruction restores exact records and stated evidence, not arbitrary Method reexecution or a fresh governing conclusion. Installed verifier/generator binaries are separate exact software dependencies when their execution is requested; retaining a reading view does not promise to reinstall all source toolchains.

## 3. `retain-package`

Required request fields: request ID/idempotency key, exact root-manifest binding and bytes, ordered member bindings/original buffers, actual selected store/custody-policy binding, consumer/scope/purpose, requested deadline and limits. No destination path supplied by Define is accepted as custody authority.

Permission uses the same host-owned current authentication/authority verification boundary described in [handoff](REVIEW-HANDOFF.md#2-inputs-and-outputs), with **separate** allowed operation `retain-package`, exact store/scope/R, read/export restrictions and validity. The retention grant does not imply review or owner authority. A preparation receipt is not a retention grant.

Ordered algorithm:

1. Authenticate the actual caller and verify current scoped retention selection, real clock/revocation, source privacy/export/retention rights and effective byte/member budgets. Capture/hash the same exact manifest/member buffers under no-follow bounded reads or authenticated bounded streams.
2. Strictly decode and validate the manifest, Pack identity/binding, required graph and exact member hashes/sizes. Verify required external evidence was captured as members; reject ambiguous references. Check source/member permission and privacy before returning any restricted data or making a completion claim. No sanitization may silently alter bytes under R.
3. Acquire the owned custody-operation lock; inspect the idempotency journal. Same key plus different fingerprint conflicts. R plus identical complete members is reusable after fresh permission checks; conflicting bytes at an existing digest path are integrity failure.
4. Write missing objects to owned staging files with exclusive/no-follow creation, restrictive modes and exact size bounds. Hash the captured original bytes, flush/fsync them, publish via supported atomic no-replace link/rename semantics and fsync parent directories. Existing objects must be fully verified, not trusted by filename. Do not overwrite them.
5. Reverify the complete required set and root from the retained objects and recheck current permission/deadline/selected store identity. This check uses the buffers being verified and cannot substitute a different body after hashing.
6. Atomically publish `packages/R/complete.json` without replacement and fsync it and its directories. This is the custody commit point. The receipt binds R, exact stored member set and required subset/count/total bytes, store identity/scope, verified policy/request bindings, capture evidence and claim ceiling. It excludes itself, any future signature and governing record digests. Any signature is a separate envelope over already frozen receipt bytes.
7. Record the exact completed result in the host's bounded operation journal and return its binding. A completion receipt can be inspected after a lost response; it is not semantic admission. Any precommit interruption leaves only unselected objects/staging, never a complete package claim.

Root and members may physically exist after a failed/rejected operation. They remain unlinked/non-governing material; no automatic deletion or current-state effect follows. Retention loss/revocation/retirement is explicit policy and never a silent history rewrite. Destructive garbage collection is outside this first implementation and requires a separately authorized reachability/retention process.

If R is already complete in this same store/scope, a newly permitted request can reuse the original verified completion receipt. It does not rewrite that receipt's historical policy/request/time to match the new caller. Fresh access/reuse observations are separate journal results. All listed supplied members are checked at completion; a full later reconstruction claims the required subset explicitly, and reports any unavailable optional members separately.

The closed completion receipt fields are `schema_version`, `root_binding`, `stored_member_bindings`, `required_member_ids`, `total_bytes`, `store_id`, `scope_ref`, `store_selection_binding`, `request_binding`, `policy_observation_binding`, `completed_at`, `claim_ceiling`, `authority_effect:none`. It is a historical custody observation; its policy observation does not serve as a later read grant.

## 4. Linking the actual retained result into Lab state

Proposed locator grammar:

```text
lab-retained://<selected-store-id>/sha256/<R>
lab-retained://<selected-store-id>/sha256/<R>#/members/<escaped-member-id>
```

Store IDs are restricted ASCII identifiers selected from the caller's allowed host configuration; URI authorities are not network hosts. R is exactly 64 lowercase hex characters. Fragment selectors are defined by this resolver contract; no generic URL fetch or path fallback is allowed. Full-package resolution has no fragment. Entry references inside `pack.json` add an explicitly typed member-and-RFC6901-selector binding in the Evidence/Pack reference record; they do not overload the manifest-member fragment with a second interpretation.

The manifest's `members` map gives these selectors one unambiguous domain. Member IDs use restricted ASCII identifiers without slash/tilde, so URI decoding cannot introduce a second path interpretation. Store IDs use `[a-z][a-z0-9-]{0,63}`. Noncanonical or multiply decoded forms refuse.

| Existing carrier | Exact mapping and validation |
| --- | --- |
| Source/v1 | `payload.locator = lab-retained://store/sha256/R`; `content_digest = sha256:R`; source kind identifies a frozen Definition Pack package; captured-at/provenance refs bind actual capture/custody evidence, including the exact completion receipt digest. Ordinary owner/scope/evidence/challenge/relation fields remain required by the carrier. |
| Evidence Set/v1, if selected | `source_refs` identify exact Source revisions; `item_refs` are supported retained member URIs or exact independently valid evidence refs; coverage and limitations retain their actual scope. Deep entry selectors remain typed records inside the verified Pack. |
| Work/v1 | `output_refs` include the selected Source and optional Evidence Set revision refs. Current completion state is whatever the Work's actual applicable evidence/owner rules support; saved bytes do not finish the incident. |

These existing fields are strings; schema shape alone does not validate reference meaning. The successor installs a closed carrier-field resolver mapping for Source `locator/content_digest/provenance_refs`, Evidence Set `source_refs/item_refs`, and Work `output_refs`. It distinguishes candidate cohort refs from admitted current/historical refs, verifies exact header/digest/selector and typed reference class, and rejects unsupported classes. No wildcard global Relation Kind or inferred `has-pack` edge is added. Full generated records must also pass existing required relation signatures/allowed endpoint pairs; no relation declaration is invented merely to satisfy schema presence.

The custody-receipt reference class uses `retention-receipt:<store-id>:<R>:sha256:<D>`, where D is the raw digest of the exact completed receipt. The resolver maps it only to that selected store's `packages/R/complete.json`, verifies D and its R/scope/member bindings, and rejects a different receipt. Thus an admitted Source pins the custody evidence as well as R. Receipt contents are public-to-that-scope provenance bindings, not embedded private policy bodies or credentials.

Important noncycles:

- New Source/Evidence/Work bodies, review results and owner decisions are **outside** R; they are created after the retained package is frozen.
- The retained root may include historical input Work/Source records. It cannot include a future output record that itself hashes or names R.
- Cores bind materialized Source/Work bodies only after R and actual custody evidence exist. Later review evidence may be retained as a new attachment/package with lineage; it never mutates R.

The existing host publisher is the only governing commit boundary. Before applying Source/Work targets, it rechecks the actual complete retained receipt and required member closure under the qualified store contract, plus exact owner effects, expected head and dependency closure. Bytes are retained **first**. Governing epoch publication happens **second**. A rejected review leaves unlinked bytes; it cannot leave an admitted record pointing to a never-completed package.

## 5. `read-retained` and cold reconstruction

Required read inputs: exact selected Work/Source/Evidence headers and source cut (or explicit authorized candidate-inspection posture), permitted store selection, R, purpose `frozen-pack-inspection`, requested members/selectors and limits. Historical references are explicit; no current alias is silently substituted.

1. A new host process/Session obtains its own actual fresh permission. Resolve exact Work→Source/Evidence references from selected Project State/Context or an explicitly permitted historical/candidate scope. Do not reuse old review credentials or restore machine RAM.
2. Validate the Source locator grammar and `content_digest`, store allowlist/scope and new caller's read permission. The locator is identity, not permission. Verify the completion receipt/request/store identity under the selected custody contract.
3. Read/hash the root object by R through anchored no-follow owner/mode/size-checked file descriptors. Strictly parse the same returned bytes. Derive the required set from the immutable manifest; compare it with the completion receipt.
4. For **full reconstruction**, load and verify every required member, including exact `pack.json` digest and all required dependencies. Recheck directory/leaf identity and digest before returning each captured buffer. The complete result/new local directory is not published until the full set verifies; any streamed prefix is provisional and cannot count as success. Bounded member inspection may return a subset, but its result explicitly says `partial-member-inspection` and cannot claim full reconstruction.
5. Check the Pack/file/entry identity, revision, RFC6901 selector and canonical-entry digest under the selected encoding contract. Restore exact frozen member bytes to a requested **new** local directory with safe logical paths and supported no-replace publication, or expose a complete verified read bundle. No regenerated Pack or overwrite is allowed.
6. Return a reconstruction observation binding R, Pack digest, selected governing record/source cut, freshly authenticated consumer/policy, verified required set, missing/blocked details, purpose and limits. Current-use readiness remains separate. A historical FAIL, open question or unadmitted working meaning retains its original status.

If any required byte is absent, altered, unauthorized or unsupported, return the exact affected bindings with `reconstruction-incomplete` or the appropriate refusal. Do not silently downgrade the required set, fetch another version, regenerate a missing body, or report success based on the root digest alone.

The separate `cal.define.reconstruction-observation/v1` has closed fields `observation_id`, `root_binding`, `pack_binding`, `governing_record_bindings`, `source_cut`, `consumer_binding`, `permission_observation_binding`, `verified_member_ids`, `missing_or_blocked_bindings`, `purpose`, `outcome`, `limits`, `observed_at`, `limitations`, `authority_effect:none`. `outcome` is `complete-required-closure`, `partial-member-inspection`, `reconstruction-incomplete`, `refused` or `unsupported`. Only the first can publish a complete reconstructed output directory; `pack_binding` may be null on a refusal before body access.

## 6. Lifetimes, crash boundaries and limits

| Boundary | Required behavior |
| --- | --- |
| Review workspace ends | Durable retained root is independent; no workspace-object locator is its identity |
| Session ends | Short memory expires; persisted package is explicit Work/custody state |
| Access grant expires/revokes | New reads/writes refuse; retained byte identity is unchanged |
| Custody complete, governing publication fails | Inspect/retain unlinked material; no automatic adoption or redispatch |
| Governing commit outcome unknown | Inspect actual host epoch/receipt, then resolve its exact retained root; do not generate another root to conceal uncertainty |
| Missing/corrupt retained member after publication | Integrity/availability gap is visible in read-back; block the affected use and follow actual recovery policy |
| Existing destination | Refuse local reconstruction overwrite |

Effective bounds are the strictest selected policy and [preparation limits](../0005-amended-integration-plan/limits.json). Proposed initial root ≤256 KiB, members ≤256, each member ≤16 MiB, complete root plus **all** supplied members ≤16 MiB, maximum first-discovery traversal depth ≤64. Pack/request and native Vault inputs retain their stricter individual limits (notably 1 MiB per native material). Aggregate accounting uses distinct byte objects plus bounded manifest/control bytes; alias members cannot evade logical-member or reference budgets. Unsupported filesystem guarantees or transfer sizes refuse; no truncation or hidden TTL extension is allowed.

Custody completion is a declared fsync/no-replace local filesystem contract; power-loss resilience beyond that contract and a Product availability SLA require later measured evidence. Acceptance cases R01–R10 in [REVIEW](REVIEW.md) cover the design's required behaviors.
