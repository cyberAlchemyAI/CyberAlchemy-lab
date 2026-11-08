# Original commerce source-stage owners

These APIs turn actual captured Alch source into independently checked commerce
semantics, an inspectable review, a physically recorded explicit decision and
an original source-authoring input. They cover the wider commerce roles rather
than reducing them to the U0 Boolean-only cell.

They prepare source for subsequent construction. A source-authoring input is
not the selected `CommerceInputHandle`, a loaded profile, a native basis, an
early request, an accepted checked application or generated/imported output.
Those later stages still need their actual original owners. Source handles,
inspection JSON and matching hashes cannot be substituted for them.

## Source and semantic custody

`createCoreCommerceSourceOwner()` captures the declared physical source and
asset closure. `createCoreCommerceSemanticOwner(sourceOwner)` requires that
exact registered source-owner factory. Its `check(originalSource)` independently
reconstructs pure declarations and separate Query, Operation, Workflow and
entry producer contracts from captured text and assets. It accepts no frontend
checked-role DTO or supplied normalized-subject label.

The semantic handle is recognized only by its original owner's private registry.
Inspection returns frozen explanatory data. JSON copies, prototype copies,
proxies, another factory's handles and disposed handles reject. Currentness
checks retain actual source/root/file identity and a module-load pin over the
semantic implementation closure and the nine runtime contract resources.
Replacing code, contracts or physical files requires fresh owning code and
fresh checks; a new factory in the already loaded process cannot bless drift.

The executable subject includes the independently normalized pure semantics,
per-role subjects, source interfaces, service ownership and execution-bearing
captured configuration. Source layout/comments and capture-only source-path
directives are outside that logical subject; physical source custody still
changes when the source changes. The optional assurance subject separately
binds claim declarations and captured claim-file bytes. Inline claims, claim
file edits and a separate claim-only module do not change executable meaning.
No proof engine or formal backend is executed by these source-stage owners.

## Explicit review and decision

`createCoreCommerceReviewOwner(semanticOwner)` requires an original semantic
owner. `prepare(semanticHandle, declaredOwner)` returns an original review whose
inspection exposes the checked roles. `render(review)` includes their actual
predicates, guards, ordered control and permissions. Its digest binds declared
owner, application, original source capture, semantic/review implementation
epochs, executable subject and optional assurance subject.

Recording a decision requires all four explicit fields:

```typescript
const inspection = reviews.inspect(review);
const decision = reviews.recordDecision(review, {
  decision_id: "business-review-001",
  owner: inspection.owner,
  outcome: "accepted", // or "declined"
  reviewed_digest: inspection.review_sha256,
}, absoluteNewDecisionFile);
const accepted = reviews.requireAccepted(review, decision);
```

The request must come from the caller's explicit local choice. There is no
default acceptance. This record is a declared business decision; it does not
authenticate the declared human, grant an Auth permission, admit a profile or
authorize publication or operations. Tests record clearly named fixture choices
only and do not stand in for the user's real business acceptance.

The file is created exclusively with mode 0600 through an opened original
parent directory. Existing files, identical repeats, nonempty targets and
symlinks reject without overwriting prior bytes. Post-create failures retain
bounded residue; deleting a pathname could remove a competing replacement.
Capturing an existing decision uses strict UTF8 and duplicate-aware closed JSON.
All source/review/code/subject fields must match the exact current review.

Private decision and accepted-review registries retain original parent objects
and the file's physical identity. Same-byte replacement, byte/mode/parent drift,
deletion or disposed/stale source/review/code invalidates descendants. A decision
captured for one original review cannot be passed to another by matching hashes;
reuse requires explicit physical recapture for that current original review.

## Source-authoring input

`createCoreCommerceInputOwner(semantics, reviews)` joins exact original parents:

```typescript
const input = inputs.form(sourceCapture, semanticHandle, review, accepted);
inputs.assertCurrent(input);
const display = inputs.inspect(input);
```

All four parents must belong to the exact same current chain. A declined or
missing decision, cloned token, cross-factory handle or mixed semantic/review
scope rejects. Input inspection is descriptive data with explicit qualification:
accepted source authoring only; profile selection, native basis, early request
and checked-application construction remain required. Zero formal claims is
valid throughout this chain.

## Open Questions

EC07 still needs full obligation/service-ownership accounting and its final
integration evidence. Actual technical-family/profile selection and native
assembly remain later tasks. Public exports/build/capture and affected installed
replay are EC12 work; these source-stage APIs do not update the frozen release.
Local hosting, TDE, EVF, publication/deployment and live activation remain
deferred. This guide is candidate repository documentation.
