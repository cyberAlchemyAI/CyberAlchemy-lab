# Contract workbench: compare declared terms and keep their sources

A comparison is useful only when a reviewer can see which editions and source passages it describes. This illustrative application records two editions, compares their declared clauses and obligations, and saves an explicitly permitted review with the discussion, citations and both source editions.

The supplied example changes a payment deadline from 30 to 45 days, removes a delivery clause and adds a confidentiality clause. Bounded `filter` and `map` calculations produce the added, removed and changed clause IDs. Another calculation compares declared obligation fields. These are exact structural comparisons of the supplied records and text. They do not establish legal equivalence, enforceability or what a court would decide.

`EditionWellFormed` checks unique clause/obligation identities, the document edition attached to every clause and the clause referenced by each obligation. `ComparisonEligibility` checks that the editions belong to the same contract, the requested editions match the actual stored records, the citation list refers to supplied evidence, both compared sources remain represented, and the reviewer chose `Approve`. The `ReviewComparison` operation reads both editions through protected Queries and saves the accepted comparison atomically. A free-standing Boolean approval is insufficient.

`CitedContext` is the join with the existing ingestion and permissioned-RAG applications. Its discussion should come from a genuinely released answer; source dependency records must include both documents, even if a display cites only one. The deterministic model checks the domain relationships but cannot authenticate arbitrary JSON as original source evidence. G5 still owns the generated original-owner binding and current full-context checks. Automated extraction of arbitrary structured legal clauses is not implemented by naming this example.

The profile uses existing generic business-role bindings and the existing protected architecture. Permissions stay with each Entry, and the original Auth and SQLite owners retain execution and persistence. No new contract-workbench compiler family or external legal-service write is introduced.

`example-project.json` collects existing CLI/SDK arguments; it is not a new compiler project syntax. Compile `business-roles.profile.json` and the existing `protected-ServiceAssembly.profile.json` using the enclosing `technical-profile-source` folder as source root. Existing `profile generate-source` accepts the compiled architecture with `--business business.alch`, `--business-profile contracts/selected-profile.json`, and `--http-profile contracts/http-profile.json`.

`CitedContext` records the discussion, citations and source editions. The ordinary domain API checks their structural relationships; a human caller can supply evidence for review, so this endpoint alone does not authenticate RAG provenance. The composed path uses `createCitedDomainReview`, which accepts only an actual original generated RAG application. It reads the current released answer and every selected source edition, runs the source-selected `CitedReviewContext.FromReleasedAnswer` Mapping through the existing pure compiler owner, and invokes the original protected review Entry. The finite binding rejects a Mapping that changes the released answer, citations or source editions.

The connected examples use the text files in `fixtures/knowledge-source-*.txt` as actual original document/index inputs. Their recorded model client and independent review labels exercise ownership and execution; they do not measure real-model correctness. `cited-context.alch` and `contracts/cited-context-profile.json` select an existing bounded-value recipe; there is no handwritten answer-to-domain transformation.

```js
const review = await createCitedDomainReview({
  rag: originalGeneratedRag,
  source: {id: "1", run: "201", actor: originalRagReader},
  mapping: {
    sourcePath: absoluteExamplePath + "/cited-context.alch",
    profilePath: absoluteExamplePath + "/contracts/cited-context-profile.json",
    selector: "CitedReviewContext.FromReleasedAnswer",
    readSelector: "CitedReviewContext.FromSavedReview",
    acceptanceDirectory: existingPrivateStateDirectory,
    owner: "example-host"
  },
  target: {composition: originalDomainComposition, handle: originalDomainHandle,
           runtime: originalDomainRuntime, entry: selectedReviewEntry,
           actor: originalPermittedReviewer, readEntry: internalSavedReviewEntry,
           readActor: originalPermittedReader},
  disclosure: selectedExampleProject.cited_release
});
const acknowledgment = await review.invoke({
  request: businessReviewWithoutCitedContext, commandKey: "review-1"
});
const releasedReview = await review.read({reviewId: "3000"});
```

The technical selection in `example-project.json` contains `cited_release`: source-bound retention, an explicit `domain-review.store` policy at `local:<actual service>`, and a distinct `domain-review.read` policy at `app:<actual service>/reviews`. The operator configures these policies through the original source-release authority. Storage must be an explicitly allowed processing destination; read uses the actual protected Query's authenticated principal as recipient and requires current access to the full original source context. No `approved`, `current` or `grounded` Boolean can replace those owners.

The trusted host still supplies original runtime resources, private storage, Auth actors, producer run and explicit human review choice. The helper supplies the cited context; a caller-provided `citedContext` rejects. It authorizes the exact retained request against the original full manifest and actual store/service identity, checks currentness after asynchronous authorization and before invocation, then checks again after the original command. The write acknowledgment contains only the actual command observation, outcome kind and hashes; it does not disclose the saved discussion or source metadata.

Saved-review Queries remain original protected internal Entries. Their raw HTTP routes are deliberately absent from this example's technical HTTP profile and generated service inventory. The composed read obtains a current original Query observation, projects its saved discussion/citations/source editions using the checked `FromSavedReview` Mapping, and requires exact equality with the genuine current RAG answer. A distinct original source-release ticket authorizes the entire source-bearing response to the actual Query principal. A write permission alone does not grant source-read access.

The domain store remains the atomic commit owner. If source access changes while a review commits, the helper withholds the result and preserves its actual command observation/hash; it does not pretend to roll back the completed review. Its saved row cannot bypass source revocation through a raw public read route. The composed read denies until the configured genuine source context and recipient access are current. Original source-release consumption metadata retains provenance. There is no distributed transaction, inferred independent retention grant, automatic resubmission or automatic deletion policy.

Tests cover generated API business behavior, fractional adoption rounding, section moves, genuine cited proposals, current source custody, explicit storage/read release, fake sources, changed Mapping output, original reviewer permissions, a denied reader policy, and revocation after a real observed domain commit. The model and independent-quality clients remain recorded fixtures. Graphs and bridges come from the original architecture and pure Mapping generators. G6 owns the complete clean installed tuple and consolidated result.

## Open questions

Real-provider/model quality, production Auth, actual external account/activity reads and cross-owner atomic transactions are not claimed. Arbitrary model-generated structured account or legal facts require their own typed source/domain contract; a cited discussion is not a legal finding or a verified health prediction. Formal claims are optional. Hosting, TDE, EVF, deployment and publication remain deferred.
