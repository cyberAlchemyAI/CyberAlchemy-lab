# Customer success: explain a recommendation before accepting it

A renewal recommendation should agree with the account being discussed. This illustrative application records an account snapshot, calculates a small health score from adoption and activity observations, selects an appropriate next action, and saves a permitted human review of that recommendation.

The example account has 8 active seats out of 10 licensed seats. Its two recorded activities add 5 and 10 demonstration points, so its score is 80 + 5 + 10 = 95. The percentage uses explicit floor rounding, so 1 active seat out of 3 gives 33 points rather than an inexact-division failure. No support escalation is open, so the suggested action is `Renew`. An open escalation changes the action to `SupportReview`; low adoption changes it to `AdoptionReview`. These are teaching rules, not a claimed industry standard or a real company's renewal policy.

`AccountSnapshot` and `Activity` describe business observations. `HealthScore` is a bounded calculation using `fold`. `SuggestedAction` is a typed policy. `RenewalEligibility` checks the stored account edition, the proposed action, cited evidence and the explicit review choice. `ReviewRenewal` reads the actual stored account through its protected Query before invoking the pure decision and atomically saving the review. The API cannot make a stale account edition current merely by setting an approval flag. Saved-review transport is composed with the original source-release gate described below.

`CitedContext` records the discussion, citations and source editions. The ordinary domain API checks their structural relationships; a human caller can supply evidence for review, so this endpoint alone does not authenticate RAG provenance. The composed path uses `createCitedDomainReview`, which accepts only an actual original generated RAG application. It reads the current released answer and every selected source edition, runs the source-selected `CitedReviewContext.FromReleasedAnswer` Mapping through the existing pure compiler owner, and invokes the original protected review Entry. The finite binding rejects a Mapping that changes the released answer, citations or source editions.

The supplied `business-roles.alch` selects four existing Entry roles. The original protected architecture profile generates the API grouping; the original Auth and SQLite owners execute it. There is no customer-success compiler family, new database, custom predicate interpreter, application handler or external CRM mutation. The typed local account records do not imply that HubSpot account/activity telemetry is already supported.

`example-project.json` is a readable collection of arguments for the existing profile CLI/SDK, not a new compiler project syntax. Compile `business-roles.profile.json` and the existing `protected-ServiceAssembly.profile.json` with the enclosing `technical-profile-source` folder as source root. The existing `profile generate-source` command takes the selected architecture, `--business business.alch`, `--business-profile contracts/selected-profile.json`, and `--http-profile contracts/http-profile.json`. The focused example test also resolves all business roles against those exact checked Entries.

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
