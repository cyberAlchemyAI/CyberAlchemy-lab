# Executable interface and authority contract

Status: candidate runtime protocol. Protocol schemas under `schemas/` are executable interface descriptions, not new admitted semantic Definitions or canonical Artifact Types.

| Interface | Exact contract and enforcement |
| --- | --- |
| CLI | `lab.py --help` and each subcommand's argument parser. Unknown commands/arguments fail. Protocol failures return JSON `BLOCKED` and exit 2. Reads have authority effect `none`. |
| Source profile | `profile.json`: four exact immutable vocabulary/foundation roots and one D75 operational admission root, explicit D74 consequence version bindings, declared ontology-local signatures, implementation selectors, current scope, policy, challenge and runtime materials. The generated current-State lookup is checked against the immutable D75 root, State and selected histories. It carries no replay authority. |
| Proposal | `schemas/proposal.schema.json`: closed identity/base/scope/policy/challenge/target/schema envelope. Each target declares category, operation, exact revision, current carrier, predecessor, authored bytes and independent Decision reference. |
| Type package binding | `schemas/contract-binding.schema.json`, plus `Artifact Type/v3/schema.json#/properties/registered_types/items`. Descriptor and binding must agree on kind, schema path/selector/digest. The binding declares instance identity/discriminator and exact endpoint roles. This is explicit local registration, not implicit canonical carrier admission. |
| Approval | `schemas/approval.schema.json`: exact proposal and stable Decision digests, source snapshot, base HEAD, scope/policy/challenge/owner/store and Ed25519 signature. Applying needs only the provisioned public key. |
| Store configuration | `schemas/store-config.schema.json`: explicit local operator boundary and allowed effects/categories; immutable binding through genesis/HEAD/transactions. Private keys are not stored. Local filesystem custody of this configuration is the trust root. |
| Commit pointer | `schemas/head.schema.json`: exact sequence, committed transaction digest, configuration/source bindings and seal. One atomic replacement is the visibility point. |
| Transaction | `schemas/transaction.schema.json`: immutable genesis or admission envelope. Replay rechecks signatures, source identity, sequencing, expected predecessor, target validation, exact Decision cores, deterministic consequences and projection digest. |
| Consequences | Existing current Project State/v2, both Project history/v2 carriers, Admission Transaction/v1, Generated Output/v2, Decision/scope/bundle/checkpoint/authority boundary, and six current Typed Relation records. The runtime validates generated records with their frozen admitted schemas. |
| Queries | Nodes preserve independent source/effective/domain/runtime/session facets; edges distinguish ontology-local interpretation from global Typed Relation projection. Every returned path has evidence and preserves the edge's actual direction. Limits are depth ≤20, nodes ≤1000, edges ≤4000; defaults 4/100/200. Stale inputs yield no confirmed current paths. |
| Session context | Existing current Context View, Ontology, Ontology Node/v2, Ontology Edge, Ontology Cut/View and Agent Instance/Session carriers. Context TTL is 1–86400 seconds; memory ≤100 notes, each ≤10000 characters. HEAD change/source drift/expiry/close blocks reuse. No session working memory enters the durable transaction chain. |

## Stable cores and deterministic consequences

Decision cores bind exact authored targets and independent effects before outputs exist. Their digests and the complete proposal digest are signed together. The successor state digest derives from predecessor state, proposal and cores. Histories then bind this state and the authorization. The Admission Transaction binds final state/history/registry outputs; the application receipt binds all final record digests. This ordering prevents a receipt/Decision/state hash cycle and another approval for deterministic consequences.

The Generated Output's declared index covers authored targets and pre-consequence subjects. Its scope is explicit; it is not the complete current catalog or a replay source. The complete catalog is reconstructed from all committed records, including governance consequences and generated Typed Relations. The receipt binds every generated record, and runtime source selectors identify their exact location in the immutable transaction envelope.

## Semantic and governance separation

Semantic events bind changed material and predecessor/result state. Governance events bind the signed authority, scope/policy/challenge and exact semantic tuple; they do not patch semantic state. Each stream retains its own contiguous cursor and digest chain. The immutable envelope commits both records atomically. Their records and transaction inputs are replay sources; indexes, graph snapshots and context packets are disposable projections.

## Declared extension discipline

The existing source vocabulary remains closed. A new local Relation Kind needs a unique typed axis, explicit exact endpoint pairs, qualifier schema, current carriers for both endpoints, and directional role declarations on each affected carrier. New Typed Relations require current schema support, resolved exact endpoint revisions and closed qualifiers. A bundle may contain the required type successors, Relation Kind and connection together; authorizing that bundle never invents an undeclared endpoint. An unrelated existing unresolved source reference remains a visible diagnostic rather than an alias.

## Scope and limits

This implementation manages one source-profile-bound local branch at a time. It authenticates the provisioned local operator, not external organizational authority, general delegation, network identity or all policy semantics. It reports unknown confidence, permission, realization and liveness rather than inferring them. Source-profile evolution and repository promotion require explicit review; no background service, multi-host writer or external execution is implied.

## D75 successor profile

This candidate selects D75 State and both history cursors at 5. It applies the exact D75 artifact and Typed Relation admission overlays after the frozen D74 consequences. Older State revisions and the D74 history revisions become historical. The D74 registries remain the semantic vocabulary anchors. The source loader binds each of the 17 D75 records to its exact admitted current carrier; the successor validation suite checks their schemas. Six global connections must satisfy the existing Typed Relation and Relation Kind contracts.

The runtime package version `implementation:cyberalchemy-lab:operational-runtime:v1@v1` and the admitted Implementation artifact revision `implementation:cyberalchemy-lab:operational-runtime:v1@decision-0075` remain distinct. The implementation-symbol bridge selects only that exact admitted artifact revision. It does not imply runtime activation, product realization, or admission of this v2 executable.

The default store is `.local/lab-runtime/v2/store`. Initialization requires this executable's exact profile. A store bound to another profile remains inspectable as historical/stale, with no confirmed current traversal; transaction review, authorization, application and Agent context require the active exact profile. Recovery can repair the frozen committed branch without rebasing it. An upgrade requires an explicitly provisioned fresh branch; local history is never copied into a new authority boundary automatically.
