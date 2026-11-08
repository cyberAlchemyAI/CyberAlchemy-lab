# Generate a Rule, Operation, Mapping and calculated decision

This is the historical C01–C08 source-development walkthrough. Its candidate
status and repository-relative commands describe those stages, not the current
installed archive. For an installed consumer, start with
[profile generation](PROFILE-GENERATION.md) and
[business-only applications](BUSINESS-APPLICATIONS.md).

C01 is the first cumulative generic slice: a typed Bool record and an explicitly authored Bool Rule generate a standalone Node ESM module. C02 adds an Operation that calls that Rule and returns a typed outcome. C03 adds a Mapping that shapes the result. Later phases add calculations and application effects. Current construction/review status is recorded in `implementation/craft-alchlang-generic-applications-2026-10-18-r5/PROGRESS.json`; this guide alone is not a qualification receipt.

For installed, ready-to-copy inputs, the AlchLang public core package includes
`examples/generic-rule` and `examples/generic-decision`. Its installed
`docs/GENERIC-APPLICATIONS.md` gives commands that need no private tutorial tree.
The decision project covers this pure cumulative chain through state proposals;
this guide retains the earlier repository walkthrough and later API/Workflow
contracts for their respective scopes.

The business source is ordinary Alch syntax:

```text
module ReviewDesk version 1

value-object Request:
  verified Bool
  flagged Bool

rule IsVerified:
  input request Request
  expression request.verified
```

There is no required formal claim. `false` is a valid Rule result; an invalid input or exhausted execution budget is a typed failure. Field names have no implicit meaning: changing the expression to `request.flagged` changes what the Rule checks.

## Source, limits and profile

Use the complete authored example at `implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C01/`. It contains three inputs:

- `business.alch`: domain data and executable business condition.
- `contracts/bounds.json`: the exact source-declared byte, item, iteration, AST, call-depth and fuel budgets. Its current envelope is the retained `craft.commerce-compute-bounds/v1-candidate` format; the name does not restrict business domain names.
- `profile.json`: the versioned `node-esm` profile with `Rule` and `record-bool` capabilities. Its limits must equal the authored bounds; a profile cannot silently change business execution limits.

The compiler generates the technical application root. Users do not write service bindings, a synthetic HTTP entry or a JavaScript business callback for this slice. Profiles currently select the qualified pure recipe; an unsupported target or capability fails before output. These source development tools have not yet been qualified as a clean-installed public package.

## Generate and invoke

The tested generator uses Linux x64, Node 26.8.1 and the existing pinned tsx dependencies. Its atomic publication helper is platform-gated to Linux x64; other generator platforms are not qualified. The emitted Rule uses Node builtins, but broader consumer runtime/platform compatibility still needs its own qualification.

From the repository root:

```bash
REPO="$PWD"
EXAMPLE=$(mktemp -d)
cp -R "$REPO/implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C01/." "$EXAMPLE/"
cd "$REPO/craft/projects/domainspec-v2/impl/cli"
node --import tsx "$REPO/language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/generic-composition-cli.ts" generate --source "$EXAMPLE/business.alch" --profile "$EXAMPLE/profile.json" --rule ReviewDesk.IsVerified --out "$EXAMPLE/output" --accept-local-review example-owner
cd "$EXAMPLE"
node --input-type=module -e 'import {evaluate} from "./output/rule.mjs"; const result=evaluate(new TextEncoder().encode(JSON.stringify({request:{verified:true,flagged:false}}))); console.log(result.ok ? JSON.parse(new TextDecoder().decode(result.wire)) : result.error);'
```

The final command prints `true`. Change `verified` to `false` to obtain `false`. A string such as `"true"` fails type validation. Generated runtime input/output are UTF-8 JSON bytes; the result has an explicit `ok` discriminator.

`--accept-local-review example-owner` is an explicit local acceptance of the captured source/profile review for this invocation. The name is a local decision label, not authenticated identity or an external approval. The SDK exposes separate prepare, review, accept and generate operations so callers can inspect the exact review digest before accepting. Forged handles, changed captured files and mismatched/declined decisions cannot authorize generation. A sibling decision JSON records the exact local decision. Use a fresh output path for another invocation.

The output contains `rule.mjs`, `business-graph.json`, `system-graph.json`, `business-system-bridge.json` and `manifest.json`. The executable module uses Node builtins and runs outside this checkout. Graphs and lineage cover only the actually checked/generated C01 structures. Full services, transport wiring and complete application composition remain later steps. Output publication uses the existing exclusive atomic directory writer; an existing destination is not replaced.

## Extend the Rule with an Operation

The complete C02 input project is in `implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C02/`. It keeps the C01 record and Rule and adds:

```text
operation ApproveRequest:
  input request Request
  output Request
  on not IsVerified(request) reject unverified
  return request
```

The profile explicitly adds `Operation` to its `Rule` and `record-bool` capabilities. Bounds still belong to the business input and must match the profile. The C01 profile continues to support Rule-only input; it does not silently acquire Operation support.

From the repository root, generate the Operation using the same review flow:

```bash
REPO="$PWD"
EXAMPLE=$(mktemp -d)
cp -R "$REPO/implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C02/." "$EXAMPLE/"
cd "$REPO/craft/projects/domainspec-v2/impl/cli"
node --import tsx "$REPO/language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/generic-composition-cli.ts" generate --source "$EXAMPLE/business.alch" --profile "$EXAMPLE/profile.json" --operation ReviewDesk.ApproveRequest --out "$EXAMPLE/output" --accept-local-review example-owner
cd "$EXAMPLE"
node --input-type=module -e 'import {evaluate} from "./output/operation.mjs"; for (const verified of [true,false]) { const result=evaluate(new TextEncoder().encode(JSON.stringify({request:{verified,flagged:false}}))); console.log(result.ok ? JSON.parse(new TextDecoder().decode(result.wire)) : result.error); }'
```

The decoded outcomes are:

```json
{"tag":"Returned","fields":{"value":{"verified":true,"flagged":false}}}
{"tag":"Rejected","fields":{"code":"unverified"}}
```

These are business outcomes inside a successful evaluator result (`ok:true`). A guard with a failure action, such as `on not IsVerified(request) fail unverified`, produces `{"tag":"Failed","fields":{"code":"unverified"}}` when triggered. `fail` and `reject` are guard actions in the retained grammar, not standalone statements. Invalid input or exhausted fuel instead produces `ok:false` with a typed evaluator error. Do not turn an evaluator error into a false Rule or a business rejection. The Operation and every called Rule share one execution budget; later guards do not run after an earlier rejection.

C02 admits guards, conditionals, explicit return/reject/fail, Bool values and the same flat Bool records. It calls actual declared Rules. Local `let` steps, calls to other Operations, callee error handlers, Mappings and all storage/network/event/workflow effects are outside this slice and reject before output. A technical outcome type is generated for the three tags; this does not introduce general business Enum support. Independent compiler construction bounds also reject excessive lowering before recursive freezing or serialization; increasing business budgets cannot disable those checks.

Select exactly one `--rule` or `--operation`. Operation generation emits `operation.mjs` plus the same graph/bridge/manifest files. Its trace binds the original Operation and Rule, with the compiler-generated outcome labeled technical. This remains source-tool qualification on the platforms described above; it does not qualify installed archives, stateful operations or an API listener.

## Extend the Operation with a Mapping

The C03 project at `implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C03/` adds `requestId UInt64` to Request and declares a Decision with `approved Bool`, `decisionId UInt64` and `manual Bool`. It retains the same IsVerified Rule and declares:

```text
mapping ToDecision:
  input request Request
  target Decision
  total true
  field decisionId <- request.requestId
  field approved <- request.verified
  field manual <- false

operation ApproveRequest:
  input request Request
  output Decision
  on not IsVerified(request) reject unverified
  return ToDecision(request)
```

The profile adds `Mapping` and `record-uint64` explicitly. UInt64 values cross the JSON boundary as canonical decimal strings, such as `"42"`; ordinary JSON numbers do not replace that exact integer encoding.

Copy the C03 tutorial instead of C02, keep `--operation ReviewDesk.ApproveRequest`, and supply `{"request":{"verified":true,"flagged":false,"requestId":"42"}}` to `evaluate`. Its decoded result is:

```json
{"tag":"Returned","fields":{"value":{"approved":true,"decisionId":"42","manual":false}}}
```

False `verified` still produces the declared `Rejected` outcome before the Mapping executes. To generate the Mapping on its own, select `--mapping ReviewDesk.ToDecision` instead; invoke `mapping.mjs` with the same input and receive the Decision record directly. The SDK also exposes `evaluateReference(handle, {mapping: "ReviewDesk.ToDecision"}, inputBytes)` after the same current accepted review. This uses the existing reference evaluator and returns the same wire/error/fuel interface as the generated module.

Field assignments execute in their authored order, independently of the Decision field declaration order. A leading `preserve decisionId, approved` copies those fields in that listed order before explicit assignments; preserve requires exactly one input of the target record type, and copied/assigned fields must be disjoint and cover the target. The retained grammar also requires at least one explicit field assignment after preserve. Equivalent explicit copies have identical evaluation and fuel charges. The compiler implements this policy with ordered typed bindings and a canonical final record, under `craft.generic-ordered-mapping/typed-lets-v1-candidate`. Binding and variable evaluation consume the shared fuel budget. Legacy Mapping semantics remain on their existing path.

C03 admits flat Bool/UInt64 records, scalar projections/constants and supported whole-expression Mappings. Cases, preconditions, arithmetic, invariant-bearing destinations and richer types remain unsupported at this phase. Calculation and invariant error behavior must be verified when C04/C05 add those capabilities. Successful C03 execution establishes the composed Rule → Operation → Mapping path, not full Mapping or application completion.

Generated graph identities distinguish three subjects. `mapping_semantics_sha256` identifies the lowered pure functions, types and limits. `executable_semantics_sha256` also includes the checked Operation behavior. `projection_sha256` identifies the source and assignment trace. A formatting-only edit changes source provenance without changing executable behavior. The legacy `semantic_sha256` remains the legacy checker's identity; it does not replace the generic ordered-execution identity.

## Add Calculations and a Policy

The qualified C04 tutorial at `implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C04/` keeps the same verification Rule and Operation. It adds `amount UInt64` to Request, `score UInt64` to Decision, and two declared Calculations:

```text
calculation BaseScore:
  pure
  input request Request
  result UInt64
  expression request.amount

calculation PriorityScore:
  pure
  input request Request
  result UInt64
  expression request.amount + 10

policy SelectScore:
  input request Request
  result UInt64
  ordered-cases:
    flagged when request.flagged -> PriorityScore(request=request)
    otherwise -> BaseScore(request=request)
```

The existing Mapping adds `field score <- SelectScore(request)`. The Operation still checks IsVerified and returns ToDecision(request). For a verified, flagged request with amount `"30"`, the expected score is `"40"`; without the flag it is `"30"`. An unverified request returns the existing rejection before the Mapping executes. No undeclared computation name supplies any behavior.

The profile explicitly adds Calculation and Policy. Keep the Operation selector for the complete example, or select exactly one `--calculation ReviewDesk.PriorityScore` or `--policy ReviewDesk.SelectScore` for the standalone module. `calculation.mjs` and `policy.mjs` expose the same byte-oriented `evaluate` API and return an exact UInt64 decimal string. The SDK accepts the matching `calculation` or `policy` selector for reference evaluation.

This phase supports checked UInt64 `+`, `-`, `*` and `/`, numeric comparisons, and ordered Policy selection. Calculation and Policy results must be UInt64; their parameters may be Bool, UInt64 or the supported flat records. The first matching Policy case chooses its declared Calculation; otherwise is mandatory. Unselected actions do not execute, while static admission checks every branch. Overflow, underflow, division by zero and inexact division remain typed evaluator errors. Division rejects an inexact result by default; a Calculation may explicitly select floor or ceil rounding. Each called Calculation retains its own rounding choice. Source-level callee error handlers remain unsupported and are rejected. Richer types and collections belong to C05. C04 passed its independent 162-case cumulative run and review; exact receipts are linked from the implementation PROGRESS.json.

## Add validated items and collection calculations

The bounded C05 implementation extends the same Operation with `List<Item,8>`. Its runnable example files are in `implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C05/`. That directory includes business source, a selected profile, explicit computation bounds and `input.json`. C05 passed 261 cumulative independent tests on source freeze002; its generated tutorial also executes outside the checkout. Exact receipts are linked from the implementation PROGRESS.json.

The business source declares each transformation:

```text
calculation EligibleItems:
  pure
  input request Request
  result List<Item,8>
  expression filter(request.items,item:Item => item.eligible)

calculation Scores:
  pure
  input request Request
  result List<UInt64,8>
  expression map(EligibleItems(request),item:Item => ItemScore(item))

calculation Total:
  pure
  input request Request
  result UInt64
  expression fold(Scores(request),0,total:UInt64,score:UInt64 => total + score)
```

`ItemScore` is a declared Calculation that multiplies the item's amount by two. The existing Policy selects the normal or priority total. The Mapping builds a validated Decision containing scores, the total, a sorted item list, a payload Enum and an optional Note. For the supplied input the expected scores are `["4","8","8"]`, total is `"20"`, and the sorted item identifiers are `["2","4","3"]`. Flagging the request changes the selected total to `"30"`; failing the verification Rule produces the existing rejection.

Collection calculations use explicit finite bounds. The generic profile adds `bounded-values` and `bounded-collections`; it uses `craft.generic-compute-bounds/v1-candidate` with computation schema `craft.generic-computation/v1-candidate` and semantics `ordered-metered-generic-v1-candidate`. Earlier profile sets retain their earlier versions and supported types. The C05 contract includes bounded map, filter, fold, indexed-fold, range, repeat, while and until forms, with numeric, lexical and natural sorting. Each sort key states its direction and comparison mode. Equal keys retain input order; all authored key expressions are evaluated before comparisons.

`append(items,item)` creates a fresh bounded list. It evaluates the list, evaluates and validates the item, then checks the declared capacity before allocating output. A bad item therefore still fails when the list is already full. `append` is reserved in generic mode and cannot also name a callable constructor or function. Its checked representation retains the list's authored type and capacity; current length cannot substitute for that capacity.

ValueObject invariants apply during decoding and construction, including Mapping destinations. Invariant arithmetic rejects inexact division regardless of the caller's rounding; an explicitly called helper retains its own declared rounding. Structural equality and `all-unique-exact` compare supported nested values rather than object identity, and their work consumes the configured resource budget. Directly nested Optional types reject; an optional record containing optional fields is supported. Bounded Unicode strings and the existing ASCII finite-pattern subset are separate constraints.

C05 qualification covers source SDK/CLI generation, reference/generated agreement and portable generated execution on one captured source candidate. Installed C05 archives, persistence and later effects remain separate stages; this does not close the full application plan.

## Add a state proposal

The qualified C06 tutorial extends the same request with its current `ApprovalState` and an `ApprovalSignal`. Its profile adds `StateMachine` to the bounded-values capability vector. Qualification combines the 261 predecessor checks that passed in the original C01–C06 run with all 52 C06 checks passing after a reviewed test-assertion correction on unchanged product source. The original failed receipt is retained; this is composed evidence from separate runs, not a fresh 313-case run. See the implementation PROGRESS.json for receipts.

The source declares the guard, machine and result-producing Calculation:

```alch
rule CanApprove:
  input state ApprovalState
  input event ApprovalSignal
  expression state == Draft and event == Submit

state-machine Approval:
  state ApprovalState
  input ApprovalSignal
  initial Draft
  terminal Approved
  transition Draft Submit when CanApprove(state,event) -> Approved
  transition Draft Submit when true -> Review
  transition Approved Hold -> Approved
  otherwise stay

calculation ProposeApproval:
  pure
  input request Request
  result outcome<ApprovalState,Bool,0>
  expression Approval.propose(request.state,request.signal)
```

`ToDecision` adds `field proposal <- ProposeApproval(request)` while retaining the earlier scores, total and sorted items. The expected Draft/Submit result selects the first matching transition to Approved. A supplied Review/Cancel follows `otherwise stay` and remains Review; `initial Draft` does not reset existing input. The complete declarations and input are in `implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C06/`.

Machine controls must be enums whose variants have no payload. Other business records may still use payload enums. A terminal state may have an explicit self-transition, but an authored edge to another state rejects during checking even if its guard is false. Guards run in source order, and an unselected later guard does not execute. Guard evaluation errors remain distinct from a typed machine rejection or an Operation rejection.

The proposal is a returned value with `tag`, `state`, `intents`, `machine`, `branch` and `reason`. This phase admits only zero intents. It does not persist the new state. Select the complete example with `--operation ReviewDesk.ApproveRequest`, or its proposal Calculation with `--calculation ReviewDesk.ProposeApproval`; no direct StateMachine CLI selector is required.

## Add stored records and protected reads

C07 supplies protected persistent reads to the cumulative example. The source suite passed 462/462, and the separate epoch-C07-003 installed package suite passed 34/34. The installed tutorial also returned its expected decision. These receipts qualify the selected private candidate; final closure and exact limitations are recorded in the C07 evidence and reviews directories. Its files are in `implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C07-005/`.

The earlier `ApproveRequest` Operation, its verification Rule, Mapping, calculations and state proposal remain in the business file. An Entity stores a Request. A Query selects it by its declared identity, and a read-only Operation invokes that protected Query before calling the original approval Operation:

```alch
entity StoredRequest:
  id UInt64
  reference UInt64
  version UInt64
  value Request
  identity id
  unique reference

query ReadRequest:
  input id UInt64
  source stored StoredRequest
  output optional<Request>
  where stored.id == id
  project stored.value
  on-missing return none
  on-unavailable fail read-unavailable

operation ApproveStoredRequest:
  input id UInt64
  output Decision
  read request from ReviewDesk.ReadRequestEntry(id=id)
    on-missing reject request-not-found
    on-unavailable fail storage-unavailable
  return ApproveRequest(request)

entry ReviewDesk.ReadRequestEntry:
  invokes ReviewDesk.ReadRequest
  interaction request-response
  access:
    authenticated customer
    permission review.read
    auth-resource review
    auth-action read
    auth-scope review-desk
```

The complete example also declares the parent `ApproveStoredRequestEntry` with its own `review.approve` permission, and a second Query and Entry for the unique reference. Permission stays on each entry. A parent permission does not grant the child Query permission. The selected profile supplies service ownership, SQLite layout, canonical key encoding, generated Auth context and logical entry wiring. The author supplies the domain fields, key choices, conditions, projections, failure behavior and permissions.

The CLI selects this composition with `--entry ReviewDesk.ApproveStoredRequestEntry`. Generation emits `application.mjs`, the captured model, `storage/schema.json`, `business-graph.json`, `system-graph.json`, `business-system-bridge.json` and `manifest.json`. The generated adapter imports `@domainspec-v2/cli/generic`. It carries the selected package name/version and semantic revision through its recipe; opening it reconstructs the captured source and requires a fresh explicit local review. A prior serialized review cannot authorize a new owner. The exact epoch-C07-003 archives and selected native assets passed their separate independent installation checks. That evidence does not qualify another archive or platform.

The generated facade retains physical identities for the model, adapter, manifest and other generated artifacts. Changing or replacing those files invalidates existing handles. Replacing the accepted review also invalidates an already-open runtime. The SDK's `reachable_operations` inspection exposes an inert dependency projection for comparing the original Operation across stages; it grants no execution rights.

The isolated tutorial uses the separate testing API to create an Auth fixture and load a fresh store once, then closes and reopens that store for application invocation. It is not a production identity setup. The selected native asset currently targets Linux x64 with glibc 2.43. C07 exposes logical request-response entries directly; HTTP exposure and business writes are subsequent steps. The returned state proposal does not persist a transition.

## Commit the decision atomically (C08 candidate)

C07 returns a state proposal. C08 extends that same application by storing the proposed state and its command result together. The existing `IsVerified`, `ApproveRequest`, calculations, Policy, Mapping and StateMachine still define the business decision. A new `ReadStoredRequest` Query returns the complete Entity so the transaction can track the record it observed.

The complete authored candidate is `implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C08-candidate-003/`. Its `ApplyDecision` Mapping copies the proposed state into the request while preserving the other authored fields; `CommittedDecision` returns the already computed decision. The following declaration is copied from that candidate:

```alch
operation CommitRequestApproval:
  input id UInt64
  output Decision
  read stored from ReviewDesk.ReadStoredRequestEntry(id=id)
    on-missing reject request-not-found
    on-unavailable fail storage-unavailable
  call decision ApproveRequest(request=stored.value)
  requires tag(decision.proposal) != "rejected" on-false reject transition-rejected
  transaction CommitApproval:
    atomic-participants StoredRequest
    update changed StoredRequest from stored:
      value <- ApplyDecision(request=stored.value,decision=decision)
    on-version-conflict reject request-changed
    on-unique-conflict reject identity-conflict
    on-proven-rollback fail storage-rolled-back
    on-unknown-commit fail outcome-unknown
  return CommittedDecision(stored=changed,decision=decision)
```

`read` calls the declared child entry with its own permission. `call` invokes the existing pure Operation. `update ... from stored` binds the write to the observed Entity. The named transaction declares its participants and how the business operation handles conflicts, proven rollback and unknown commit. Its final Mapping is checked before commit, so an invalid final result cannot leave a successful business write behind. These are the candidate contract's guarantees; full independent runtime and installed-archive qualification remain pending.

Select `craft.generic-transaction-profile/v1-candidate` in `profile.json`, with the declared application namespace, service ownership, transaction bounds and capabilities shown in the complete example. The technical realization is `sqlite-atomic-command-values/v1-candidate`. The profile supplies hidden revision tracking, transaction storage and the command journal. The authored `version` field is ordinary business data and remains 7 in this example; concurrency uses the separate generated revision.

### Generate and invoke the candidate

Select `--entry ReviewDesk.CommitRequestApprovalEntry` with the source CLI. It generates `application.mjs`, the captured model, storage description, business graph, system graph, business-system bridge and manifest. The application facade reconstructs the captured source and requires a fresh local review before opening its runtime. Source CLI generation is independently checked; the current C07 archives cannot execute this transaction profile.

The command runtime adds `prepareCommand`, `executeCommand` and `inspectCommand`, and overloads the existing `authorize` and `consume` methods for command handles. Use the exact calls in `invoke.mjs`: the host supplies a fresh original Auth actor and metadata `{ client_key: "approval-23-original" }`. Handles are bound to their original owners and consumed according to their phase; serialized objects do not substitute for them.

A command's stable identity includes application namespace, service, authenticated subject, root entry and client key. Retry the same command with the same key and payload. A successful replay returns the recorded decision after current root and child permission checks. The same identity with a different payload is a conflict. The key grants no access and is bounded to 128 Unicode scalars and 128 UTF-8 bytes, with no normalization. Command preparation captures the metadata value; later caller mutation cannot change the accepted key.

If commit disposition is unknown, a fresh authorized attempt can inspect the durable command result. Do not equate an exception or a connection flag with a proven rollback. The complete tutorial separates commit, replay, inspection and an ordinary protected read, each with fresh application/Auth ownership after close and reopen. Its fixture grants and starting rows are isolated test setup, not production identity provisioning.

### Qualification and remaining work

The isolated C08 source/plan owners, SDK generation, source CLI and public command types have bounded independent acceptance. Implementation-owned smoke runs exercised commit, fresh-process/fresh-Auth replay and inspection with unchanged stored state on replay. Those smoke runs do not replace independent transaction, concurrency, fault, crash or installed-package tests. Their commit took about 372 seconds, so runtime performance remains an open issue.

The current session repair separately addresses repeated principal projection and child Entry disposal checks. Its successor runtime results must be assessed before accepting that version. This document is an isolated candidate afterimage; it does not claim C08 closure or availability in published tools. Formal claims remain optional, and local hosting, TDE, EVF, deployment and publication remain deferred.

## Connect a checked HTTP profile to the generated application

The HTTP composition API takes the application profile and transport profile
separately. The application profile selects storage and execution semantics;
the HTTP profile selects routes and response mappings for the same checked
entries. Permissions remain on the entries in the business source.

~~~js
import path from 'node:path';
import {createGenericHttpCompositionOwner} from '@domainspec-v2/cli/generic';

const owner = createGenericHttpCompositionOwner();
const handle = await owner.prepare({
  sourcePath: path.resolve('business.alch'),
  profilePath: path.resolve('contracts/selected-profile.json'),
  httpProfilePath: path.resolve('contracts/http-profile.json'),
});
~~~

Review and accept that handle using the same explicit local source-review
flow shown above, then generate the selected entry. The generated
application's owner exposes the checked route binding too:

~~~js
import {createGeneratedApplicationOwner} from './generated/application.mjs';

const application = createGeneratedApplicationOwner();
// Prepare, review, accept and open this application's runtime as above.
const handler = application.bindHttp(applicationHandle, runtime, routeId);
~~~

Here applicationHandle is the accepted handle from this generated owner,
runtime is its open transaction runtime, and routeId is a declared route
identity from the selected HTTP profile. A foreign handle or runtime does
not gain authority through this method; a non-HTTP application rejects it.
The emitted entry-http.mjs also exports createGeneratedHttpHandler with
the same owner, handle, runtime and route identity.

The checked HTTP overlay also composes with admitted external-write and Event
applications. A request-response entry may use a customer or operator principal.
Service Event receivers retain their original relay-owned credentials and
cannot be exposed by changing a route in the HTTP profile.

For a selected external-write profile, an uncertain provider outcome is an
HTTP 503 fault with code ExternalOutcomeUnknown. It is not a successful
business decision or evidence that the provider did nothing. Retrying the
same original command identity with current authorization lets the durable
owner inspect the original attempt; changing the payload under that identity
is a conflict. The current concrete write realization is the selected
DemoPay-v1 capture/inspection protocol, not arbitrary payment APIs.

Committed Event emission uses the same command transaction as the business
result. Receiver permission is checked before delivery, and ACK requires the
original receiver commit receipt. Replaying the command retains its original
result and does not create a second provider effect or Event occurrence.

Binding creates an injected Request-to-Response handler; it starts no listener.
Requests still need genuine runtime-bound authentication association. Test
fixtures may use their associateRequest helper; request headers and business
Rules do not mint a principal or grant entry permissions.

Generated HTTP output includes the checked http-contract.json and a source-bound
http-plan.json. The manifest exposes the same contract under
runtime_contract.http_contract. Fresh generated owners compare both artifacts
with independently reconstructed routes. The selected executable identity binds
business and transport semantics; base_application_sha256 retains the separate
business application identity. Generate fresh preview outputs with the current
tool pair.

## Generate HTTP and optional models with AlchLang

The CLI accepts the application and transport profiles separately:

~~~sh
alchlang-generic generate --source business.alch \
  --profile contracts/selected-profile.json \
  --http-profile contracts/http-profile.json \
  --entry ReviewDesk.CommitRequestApprovalEntry \
  --out generated --accept-local-review local-development
~~~

The common createGenericCompositionOwner API likewise accepts httpProfilePath.
It selects the original checked HTTP application owner and retains the optional
formal-export methods. createGenericHttpCompositionOwner is the explicit HTTP
convenience factory.

For compatibility, --profile may name the HTTP profile itself. Its existing
application_profile must then be exactly contracts/selected-profile.json
(relative to the business source root) or selected-profile.json (relative to the
HTTP profile file). The CLI follows that one declared reference; it does not
search for another profile. Supplying this form together with --http-profile
rejects as an ambiguous double selection.

formal-export also accepts --http-profile with an admitted stateful profile.
Use the same source, additional sources and external selections as generation.
Claims remain optional. Exporting TLA+, Alloy or SMT-LIB text does not run a solver,
TDE or EVF, and bounded models retain their stated unsupported semantics.

## Open a generated Workflow through the public API

An accepted source owner or emitted application owner exposes openWorkflow.
The host supplies its original producer/receiver runtimes, original Entry
actors and an owned journal directory. Craft derives the Workflow, service,
journal identity, source/profile bindings and compatibility digest from the
accepted model. Callers do not construct a journal schema or copy a contract
into a worker.

~~~js
const workflow = await application.openWorkflow(applicationHandle, {
  runtime: producerRuntime,
  receiver: auditRuntime,
  actors: entryActors,
  journal: {
    directory: path.resolve('state/approval-workflow'),
    mode: 'create',
  },
});

try {
  const start = await workflow.scheduleStart(
    new TextEncoder().encode(JSON.stringify(input)),
    'approval-start-23',
  );
  if (start?.result.ok) {
    const claim = workflow.claimNext(300000);
    if (claim) {
      const progress = await workflow.advance(claim);
      // Continue using progress.active_claim while present.
    }
  }
} finally {
  await workflow.close();
}
~~~

Here application is the accepted generated owner introduced above, and
applicationHandle belongs to it. entryActors maps the model's Entry identities
to genuine current actors supplied by the Auth integration. The test-only Auth
fixture can create isolated actors for examples; it is not production identity
provisioning. The Workflow definition is available in
application.inspect(applicationHandle).workflow_contract.

Create mode requires a new private directory under an existing parent. After a restart, reconstruct
the application owners, runtimes and Auth, then use the same directory with
mode reopen. Reopen validates the existing journal read-only before opening
it for progress; an unrelated or incompatible database is refused. The driver
does not reset, delete or migrate that database. Claim renewal, inspection and
advance use the original journal and checked runtime. Replaced journal paths
are stale resources. close waits for started driver calls and closes its
journal; the host then closes the runtimes and Auth resources it supplied.

scheduleStart accepts bounded UTF-8 JSON bytes. Duplicate keys and invalid
UTF-8 reject before scheduling. Business input types and Entry permissions
are checked by the original generated command path. The driver starts no
listener and does not supply business callbacks or authorization verdicts.

## Workflow restart identity

A generated Workflow coordinates its declared local command, durable provider
command and Event receiver. A selected HTTP profile may expose its customer
start entry with a declared response Mapping. HTTP retry and workflow scheduling
must use the same command key to refer to the same start.

Durable journals bind the complete checked file closure, selected profile,
application contract, step contracts and workflow implementation. Physical
capture directories are temporary: a replacement process reconstructs fresh
owners and authentication, then checks that durable identity before continuing.
The journal's identity.source_capture_sha256 stores the canonical content
closure hash; the live Workflow contract separately retains its process-local
physical capture hash and source_closure_sha256. A stored hash grants no
execution authority.

After an uncertain provider dispatch, recovery inspects the original attempt
and exact request body. It must not issue a new capture merely because the
worker died. After receiver commit and producer ACK, a replacement checks the
original delivery and inbox before advancing the journal. An expired worker
lease cannot authorize another journal transition. The supported composition
uses distinct service-owned stores in one selected process; distributed
deployment and multi-worker partition tolerance are outside this slice.

Changed source, profiles or implementation are incompatible with the existing
journal. Automatic journal migration and migration of older development
journals are unsupported; an identity mismatch is a refusal, not permission to
reset or discard a store.

## Version conflicts and generated HTTP bindings

A transaction can declare `on-version-conflict reject <business-code>` to map a proven conflict to its own business rejection. If that mapping is omitted, the runtime keeps the intrinsic `ReadConflict` fault, rolls back, and the checked HTTP profile projects status 409. It does not invent a business rejection or journal a stale result. The other applicable transaction recovery channels remain explicit.

Use the generated owner's `bindHttp(handle, runtime, routeId)` or its generated `createGeneratedHttpHandler` facade. The facade delegates to that same registered owner. Raw HTTP issuer and continuation helpers are internal and are not exported by the installed public API. Regenerate earlier unpublished preview bundles after updating the tools.

After an observed commit, a failed source/owner currentness check withholds the result and preserves the committed state. Recovery uses fresh authorization and the original command identity; it must not pretend that the commit rolled back.

## Open Questions

C08–C15 extend this same construction path with atomic writes, transports, external effects, events, workflows, broader profiles and optional formal models. C07 evidence covers the selected private source and installed archives. Its installed tutorial invocation took about 383 seconds, so practical runtime performance remains open; no general latency or platform guarantee follows from passing correctness tests. Local hosting, TDE, EVF and publication remain deferred.

## Native no-effect retry scheduling

The optional registered native stage `retry` method is distinct from the existing
business continuation retry. A business continuation retry still requires
`proven-not-dispatched`; a provider response such as HTTP429 is never relabelled
as not dispatched.

A source-selected provider strategy may return the typed native observation
`{kind:'no-effect-retry', original_attempt, not_before_ms, deadline_ms}` only after
its original durable effect owner has established a definite repeatable no-effect
outcome and supplied the retry timing/budget. The worker records a
`native-no-effect-wait` commitment in the existing `retry-later` state. It does not
change the business command key, local stage attempt or business inputs. Restart
preserves the original effect reference and minimum waiting time. A confirmed-no-effect wait releases its workflow claim because no native send remains in flight; claimNext skips it until the durable due time, then obtains a fresh fence. Unknown mutations retain their existing lease/quiescence rules. Once due, fresh
Entry authorization reopens the original committed business command, a
`native-retry-resume` commitment selects the optional original native `retry`
method, and that owner rechecks exact effect identity, current authority,
provider minimum wait, root deadline and send budget before one new attempt.

Unknown native mutations stay on original-provider inspection. A terminal or
unrepeatable no-effect observation follows the existing business rejection path.
A wait past the root deadline stops without a send. Source policy must explicitly
select native retries; native resources without that supported strategy retain
retry-forbidden behavior. The generic worker supplies no SDK retry loop, provider
fallback or new effect journal. The native effect owner separately persists send
and inspection budgets; a credential owner retains its own refresh budget.

This local execution extension does not qualify a real provider or strengthen an
existing formal-model exporter. Formal claims remain optional; local hosting,
TDE, EVF, deployment and publication remain deferred. Related unresolved questions
remain in the Open Questions section of this document and the selected native
owner's README.
