# Direct typed inference and semantic observations

`index.mjs` exports `createInferenceRuntime`, `createCapabilityResource` and
`inference-port/v1`. `stages.mjs` exports `createTypedObservationStage` and
`typed-model-observation-stage/v1`. `transport.mjs` consumes the existing public
ARE native transport seam. No agent harness is needed for these direct calls.

Required behavior → reuse → delta:

- **Reuse:** `are.model-transports` native OpenAI client I/O, existing Core
  generated business schemas/decoders and original Auth/business transaction
  owners, R02 effect custody, source-release and R04 exposure allocation.
- **Extend:** selected `createOpenAIInferenceTransport` in ARE's existing native
  file adds strict Responses controls, separate embeddings and nullable usage.
- **Configure:** exact OpenAI `gpt-6-luna` text target, tools disabled,
  `text-embedding-3-small`/1536 with explicit preprocessing/generation identity.
- **New:** native typed observation join and opaque proposal stage. It delegates
  authored Rules/Policies to the original generated business Operation/Entry.
- **Unverified:** live provider/account/model quality. All recorded SDK responses
  in the focused tests are fixtures, even though they exercise real SQLite and
  actual generated Core codecs.

The current [Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs),
[Responses migration guide](https://developers.openai.com/api/docs/guides/migrate-to-responses),
[SDK control reference](https://developers.openai.com/api/reference/typescript),
[selected text model](https://developers.openai.com/api/docs/models/gpt-6-luna),
and [embedding reference](https://developers.openai.com/api/reference/resources/embeddings/methods/create)
were fetched during implementation. The selected path sends Responses
`text.format`/strict schema, `tools:[]`, `tool_choice:'none'`, `store:false` and
`stream:false`; both text and embeddings receive actual AbortSignal, timeout and
`maxRetries:0` request controls. The injected SDK must support `withOptions` and
expose the enforced zero retry, timeout and official API base URL. Unsupported
clients/targets reject before I/O. This does not claim provider data retention
is zero or that a mutable hosted model alias has immutable weights.

`projectStrictSchema` rejects unknown keywords, open or partially optional
objects, invalid numeric/collection constraints and unsupported depths. It
preserves generated bounded Unicode strings by an equivalent scalar-count regex
intersection with the original anchored pattern. Scalar roots are wrapped in a
required `{value:...}` object for the Responses object-root requirement and
unwrapped before the original decoder. Original UInt64 decimal-string bounds
remain exact. These projections are fixture/local-regex checked; actual provider
acceptance remains separately qualified. Embeddings use the generated finite
technical vector codec, never a business Float or implicit numeric conversion.

Construct `createInferenceRuntime({path,client,resource,sourceRelease,exposure,
assertCurrent,observer?,now?,policy?})`. `resource` contains trusted
`{id,provider:'openai',account,billingAccount,tenant,application,mode,
model:'gpt-6-luna',embeddingModel:'text-embedding-3-small',dimensions:1536,
preprocessing,generation,pricePolicyRevision,maxTokens,maxCostMicros?,
maxOutputTokens?,timeoutMs?,promptTemplate?,inputOverheadTokens?,runtimeId?}`.
Mode is the host-selected fixture/provider mode, never inferred from success.
The host supplies an already configured actual SDK client; no ambient network,
process environment key discovery or SDK construction fallback exists here.

`invoke({intentId,bindingId,operation,input,result_schema,decodeResult,
deadline_ms,limits,signal?,context,runId?,childId?})` receives only original
generated-host custody. Context is `{tenant,principal,fence,approvalRevision,
sourceRevision,manifest,policyId}`; source and business identity are checked by
their original owners. `decodeResult` is the original generated codec. Limits
require one model attempt and tools zero. The conservative declared token
maximum must cover prompt UTF8 bytes, selected overhead and output tokens.
The resource's trusted price-policy maximum bounds monetary admission. Unknown
or missing usage keeps the entire remaining exposure until explicit settlement.

Each call persists the exact full request/model/schema/input/template identity,
prepares its R02 attempt, reserves R04 exposure, issues a source-owned ticket,
records its source release checkpoint and dispatches through that same owner.
Responses normalize to candidate/refusal/incomplete/invalid/unavailable/unknown,
with independent nullable usage and exposure. Cache input and reasoning output
are reported as overlapping subsets, never added twice. Usage without observed
money keeps conservative cost exposure. Candidate decoding does not grant
business authority. Timeout/cancel/restart cannot create a new attempt key or
retry/fallback. Replay returns the original immutable attempt/observation.

`inspect()` exposes stable runtime/tenant/application/resource/mode identity for
the optional redacted observation sink. `assertCurrent` is checked at dispatch,
commit, awaited result decode and wrapper boundaries. `createCapabilityResource`
accepts `{controller,bindInvocation,operations?,capabilities?}`; trusted binding
overrides request fields and advertises the exact selected descriptor. It returns
`craft.native-capability-resource/v1` to the Core checked-native host.

The semantic stage constructor takes `{inference,bindInvocation,applyObservation,
assertCurrent}`. `propose` produces an opaque typed proposal. `apply` passes its
owned value/wire to `applyObservation`, which must be the original compiled
business operation. The stage contains no copied authored rule. Embedding
proposals retain model/dimensions/preprocessing/generation as one space identity.

Setup/rotation/account permissions belong to the existing selected SDK/credential
owner. API/model upgrades require reselecting exact package/schema identities and
rerunning scoped fixtures; no silent alias/provider migration occurs. Text calls
are bounded and stateless, no stored conversation synchronization is claimed.
Rebuild embeddings into a new generation before switching retrieval. Preserve
R02/source/R04 databases and inspection/account credentials through retirement;
unknown paid exposure requires reconciliation. Retention is the authored source
and account policy, not a new model cache. No automatic fallback or data deletion
is introduced. Package bytes, license disposition and final selected artifacts
are finalized by the enclosing objective; ARE remains a private unpublished
dependency and no relicensing is implied by the local adapter.

## Open Questions

Actual provider/account availability, model quality and provider strict-regex
acceptance are unrun. The root generated-host clean-consumer join owns proof of
compiled authored Rule execution and exact built package identity. The focused
stage fixture proves delegation, not a separate business-rule implementation.
Optional agent harness support remains separate from direct inference; Codex
`runTurn` is harness-backed and is not selected as a direct provider here.
