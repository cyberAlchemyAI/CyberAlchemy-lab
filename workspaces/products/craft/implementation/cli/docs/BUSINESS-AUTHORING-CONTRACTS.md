# Business authoring contracts

This file records the foundation boundary through B06.2. The [business authoring guide](BUSINESS-AUTHORING.md) owns the current successor CLI, API generation and coverage/view workflow. Candidate package versions are Core 1.3.0 and AlchLang 0.7.0-candidate.0; older archive envelopes remain unchanged.

Status: candidate business-authoring foundation; B01 data/schema epoch 1, additive B03/B05.2 normalization epoch 1, B06.1/B07.1 projection epoch 2 B04 review/decision epoch 2 and B06.2 materialization epoch 2. Authority effect: none.

The new boundary describes one structured business source with explicit requirements, typed Entities, Boolean-field definitions, ground formal claims, Rules, whole-input zero-effects Operations and public exposure. It does not infer business meaning from names or accept a requirement on its owner's behalf.

The Core-owned business-spec, business-authoring-project, business-review, business-decision, business-authoring-lock, business-lowering, operation-json-post and profile-package-v3 schemas are closed: unknown fields and unsupported vocabulary reject. Data shape validation is separate from a registered typed specification, exact decision, checked graph or executable application.

Profile v3 declares the known finite semantic recipe and technical wire/runtime conventions. It does not implement arbitrary semantics, evaluate JavaScript as a compiler plugin, authenticate an owner, grant public access or prove a claim. The existing explicit-v1/v2 path is preserved.

AlchLang receives a generated data-only TypeScript protocol mirror so source tooling can agree with Core without importing a private checkout. Original business sources and exact selected package/decision bytes remain the currentness evidence. B06.2 now produces a checked domain graph and action plan through the existing compiler owners. Request/API generation, system and bridge views, and native value execution remain later stages.

The source SDK now exports `parseBusinessSource`, `resolveBusinessSpec`, `prepareBusinessSpecFile`, their currentness checks and `disposeResolvedBusinessSpec`. Parsing retains every substantive original line; resolving checks explicit Entity, property, definition, claim, Rule, Operation and exposure references. JSON copies do not become registered specifications. File-prepared handles also check original bytes and physical file identity whenever their currentness is asserted.

Core's `profileEngine` now exports `validateBusinessAuthoringProject`, `validateProfilePackageV3`, `loadBusinessAuthoringProject` and `assertBusinessAuthoringSnapshotCurrent`. The new loader captures the selected source, decision, package, transitive dependency, asset, engine and tool file manifests in a separate v3 snapshot and exact lock. The caller supplies actual engine/tool identity files. Empty decision selection supports inspection; captured decision data does not establish acceptance. Loading imports no supplied executable package code.

The supported v3 declaration selects the existing finite zero-effects Operation runtime. Its transport limits the wire timeout to 30,000 milliseconds; the generic wire schema permits up to 60,000, so larger values pass shape validation but reject against this runtime. Source SDK checks exercise the local, shared-port and API-prefix technical variants. Accepted semantic bindings are available through the source SDK described below. Shipping successor profile packages, CLI commands and generated API wiring remain later work. These source additions do not update the prepared release archives.

The additive normalization contract now supplies `lowerBusinessFormalSemantics` and `lowerBusinessBehavior` in the Alch source SDK. Each named definition selects one explicit Entity Bool field. Its mechanically rendered formal definition and its runtime predicate map use that same field. Exact ground propositions and authored ceilings remain visible; quantifiers, functions, non-unary predicates, ValueObject predicates, unused sorts and Entity equality reject for this recipe. These checks do not prove the proposition.

Behavior normalization retains complete Entity field/type structures for Operation input/output, the one Rule guard and its exact input binding, and the whole-input result. It copies public exposure only when authored. Actor text stays informational; a failure token stays continuation metadata and does not implement authentication or a recovery Policy. Registered formal/behavior handles retain the original B02 handle, so cloning, disposal or source drift cannot produce a current normalization.

Core recipe selection consumes closed inert normalized data under its own registered snapshot. It validates finite correspondence and separates unchanged business data from captured technical conventions. The trusted public Alch-to-Core SDK join additionally retains genuine producer handles and checks both owners. A direct Core DTO is not evidence of Alch handle registration, owner acceptance or source-to-AST provenance. Later accepted materialization must preserve this producer correspondence. Recipe selection creates no accepted semantic carrier, request graph or API.

The new Core APIs are `selectBusinessAuthoringRecipe` and `assertBusinessRecipeSelectionCurrent`. Alch joins genuine producer handles with them through `prepareBusinessRecipeSelection` and `assertPreparedBusinessRecipeSelectionCurrent`, using the trusted public Core SDK. Selection dispatches by the registered recipe identifier, so a new compatible profile name or supported route prefix needs no compiler branch. Profile rules cannot replace authored tables or supply hidden business behavior. Technical metadata evaluation and actual generated output qualification remain subsequent stages.

Alch now supplies `previewBusinessSemantics(prepared, modelId)` and `assertBusinessSemanticPreviewCurrent`. A preview contains deterministic declaration bindings, status-free meaning and definition drafts, exact formal interpretations and Operation behavior bindings. It copies the requirement's prose, scenarios and boundaries and mechanically renders typed inputs/outcomes. The closed business review subject includes prospective legacy meaning digests; calculating those digests records no acceptance and produces no executable compatibility carrier. The returned ledger points to exact source clauses or explicit mechanical derivations in the symbolic `preview.json` artifact. Preview itself writes no files. Transport Mapping and technical profile choices remain outside the accepted business subject.

Core supplies `prepareBusinessAuthoringRequests(selection)` and `assertBusinessAuthoringRequestsCurrent`. Each explicit public capability produces one real identity Mapping in the existing Alch application grammar, a project intent and decoded POST request description. Every field is copied from the whole body with its unchanged declared scalar type. Public names remain exact; normalized IDs, routes and length limits are checked, with no truncation or silent renaming. The result includes Mapping metadata and mixed business/profile/adapter provenance. This preparation does not add an audience, effect, business transformation or implicit exposure.

The public Alch join `insertBusinessRequestMappings(prepared, preparation, modelId, source, coreSdk)` retains the original Alch and Core owners, verifies that both select the same captured model, checks the prospective application's Entity/Operation/claim structure, inserts the actual generated Mapping fragments, and parses them with the existing application parser. `assertInsertedBusinessRequestMappingsCurrent` checks the original producers, Core preparation, source fingerprint and insertion implementation. The source is prospective: this join does not compile a checked domain, create a request graph or grant acceptance. B06.2 invokes this insertion before checked domain compilation; B07.2 owns the request graph/plan/callable and API realization.

## Inspect and record a business decision

Core's `prepareBusinessAuthoringReview` checks the preview's complete business subject against the captured normalized model and independently validates its prospective legacy meaning hashes. `renderBusinessAuthoringReview` displays the requirements, scenarios, boundaries, definitions, formal interpretations, guards, returned data, rejection metadata, effects and public audience. The aggregate digest covers that exact business review. The definition closure lists only definitions referenced by the claims, with complete selected definition bodies included in its digest; an unused definition stays visible in the aggregate review but is outside the accepted definition set. Proposed wire/profile conventions are displayed separately and do not enter the business digest.

The public Alch join retains the original registered preview, so a Core data object alone cannot replace source-to-producer correspondence. After preparing a genuine `prepared` recipe selection through the earlier APIs, a host can use the source SDK as follows. The caller first creates its own decision directory and obtains explicit `choice.owner`, `choice.outcome` (`accepted` or `declined`) and `choice.reviewed_digest` from the displayed review; none is inferred or defaulted.

```ts
const preview = alch.previewBusinessSemantics(prepared, "delivery_ack");
const review = alch.prepareBusinessReview(preview, core);
process.stdout.write(core.renderBusinessAuthoringReview(review.review));

// Only after the host obtains the explicit decision for this displayed digest:
const recorded = alch.recordBusinessReviewDecision(review, {
  decision_id: "delivery-ack-review-1",
  owner: choice.owner,
  outcome: choice.outcome,
  reviewed_digest: choice.reviewed_digest,
}, absoluteNewDecisionFile, core);

// A decline is recordable; this guard then rejects it.
const acceptedScope = alch.requireAcceptedBusinessReviewDecision(review, recorded, core);
```

`core` above is the trusted public Core `profileEngine` SDK, never a profile-supplied callback. These source APIs do not yet add a CLI command. The tool writes the frozen decision JSON itself; users do not compose acceptance JSON. A supplied owner must match the authored owner, but the name is not authenticated identity. Selection, hashes and passing tests never create an outcome. The guard exposes the exact aggregate, legacy meaning subjects and referenced definition closure; it creates no accepted semantic carrier or executable graph.

The supported preview environment remains Node 26.8.1 on Linux x64. The recorder uses an inspected existing parent directory and exclusive creation of a new private regular file. It creates no directories or companions and edits no project, source or profile files. An occupied destination rejects unchanged, including identical repeats. If an error occurs after creation, the destination is preserved for inspection: a partial record can remain, and any concurrent replacement is preserved. There is no automatic path deletion or overwrite, because an inode check followed by unlink could race another writer. Incomplete records reject capture; use a fresh destination for a new explicit attempt.

`captureBusinessReviewDecision(review, absoluteFile, core)` explicitly captures a matching existing record, including in a fresh process or after a compatible technical profile change. A new project selection can capture that file through the existing v3 loader; editing selection state invalidates old handles and requires preparing a fresh review. The recorder itself never changes that selection. `assertPreparedBusinessReviewCurrent`, `assertPreparedBusinessReviewDecisionCurrent` and `assertAcceptedBusinessReviewDecisionCurrent` retain both owners and reject clones, disposed original producers, stale source/profile/selection bytes, changed decision bytes, physical file/parent replacement and implementation drift. Replaying a decision for a different business subject, owner, version, legacy subject or definition closure rejects. Global replay prevention and stronger identity authentication are outside this local record contract.

## Materialize and check an accepted application

After obtaining the original `acceptedScope` above, use the same captured selection and trusted compiler instance:

```ts
const compiler = await alch.loadDomainSpecCompiler(corePackageRoot);
// Prepare the preceding snapshot, selection and decision using compiler.profileEngine.
const core = compiler.profileEngine;
const requests = core.prepareBusinessAuthoringRequests(prepared.selection);
const checked = alch.prepareBusinessAuthoringApplication(acceptedScope, requests, compiler);
alch.assertPreparedBusinessAuthoringApplicationCurrent(checked);
console.log(checked.workspace, checked.graph, checked.executable.plan);
console.log(checked.lineage);
// Revoke this preparation when the host has finished inspecting it.
alch.disposePreparedBusinessAuthoringApplication(checked);
```

These are source SDK calls on Node 26.8.1/Linux x64. All Core handles must come from that same compiler instance. An accepted JSON object, an earlier preview or another SDK instance cannot substitute for the registered accepted-decision and request owners. Use a matching rebuilt Core and Alch source SDK; the prepared public archives have not changed.

`materializeAcceptedBusinessApplication(acceptedScope, requests, core)` is the pure materialization step. It rechecks the exact aggregate, every legacy meaning subject and the complete accepted definition closure before adding statuses. Each legacy meaning records the actual decision ID and corresponding exact subject; each claim includes only its referenced transitive definition closure. Unused definitions receive no accepted status. It copies the preview's declaration, Rule, formal interpretation and Operation bindings and inserts the real generated request Mapping. Mapping/transport provenance stays outside the authored business subject. The result exposes the explicit application source, profile-free compatibility source, exact pretty-JSON semantics bytes/hashes and a closed lowering ledger.

Core's `prepareAuthoringBusinessInput` independently reconstructs that compatibility input and runs the existing accepted-v2 semantic validator while retaining the original v3 snapshot, runtime package, accepted decision and request handles. It does not manufacture a v2 snapshot. The checked preparation then uses the existing semantic binding derivation, domain/action lowering, real compiler and executable-plan owner. Original business source and decision-file identities remain linked to the generated source, semantic carrier and checked graph manifest in `checked.lineage`.

Only generated project files are written to a fresh private scratch directory: at most 10,000 files, 64 MiB and 16 path components. Currentness checks cover original producers, decisions, profiles, implementation files, exact scratch inventory/content/physical identity and the graph/plan owner. Added companions, changed files, replaced inodes and disposed handles reject. Preparation compiles a plan; it does not run the business Operation or expose a server.

Disposal revokes the preparation handle and preserves scratch files for inspection. A compile failure also preserves its scratch directory and attaches `scratch_path` to an extensible error. The host owns retention of those bounded directories. The SDK performs no automatic path deletion because an inode check followed by recursive removal could race a replacement. Disposal does not revoke unrelated original review/decision owners or claim to revoke every lower-level compiler object.

## Open Questions

B04 supplies exact review and explicit decision recording/capture/guards. B06.2 consumes that genuine accepted join and supplies accepted semantic carriers, a checked domain graph and an action plan; B07.2 owns generated request realization, and B09–B11 own full qualification/docs. B07.3 owns the final CLI and selection workflow. Native value execution and generated API qualification remain later work. Existing prepared release archives and package versions stay unchanged. Local hosting, TDE and EVF remain deferred; publication remains held.
