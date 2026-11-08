# Choose public errors without changing business decisions

A business Policy decides whether an Operation may continue. An error-presentation profile decides how an already-produced rejection is explained to a caller. The distinction matters: changing a message or choosing HTTP409 must not change an approval, grant access, repeat a command or reclassify an uncertain provider write.

Craft implements this with existing Alch Enum, Value Object, Calculation, Policy, Mapping and Interface constructs. There is no ErrorMapper MetaType, new Policy syntax, per-application JavaScript error callback or second expression evaluator. Original Auth, transactions, command replay, workflow and external-effect owners remain responsible for their original decisions.

## Follow the CRM source

The complete working source is [error-presentation.alch](/home/vlad_/projects/cyberAlchemy-v2/implementation/craft-ai-reference-apps/crm/error-presentation.alch). Its profile imports the original `ContactUpdateRejection` from [journey.alch](/home/vlad_/projects/cyberAlchemy-v2/implementation/craft-ai-reference-apps/crm/journey.alch); it does not redeclare business reasons. The legacy [application-project.json](/home/vlad_/projects/cyberAlchemy-v2/implementation/craft-ai-reference-apps/crm/application-project.json) remains unchanged. Select [application-project-errors.json](/home/vlad_/projects/cyberAlchemy-v2/implementation/craft-ai-reference-apps/crm/application-project-errors.json) for the opt-in presentation/diagnostic version.

The chain is:

```text
ContactUpdateRejection
  -> SelectErrorSpec Policy
  -> SpecifyError Calculation constructs ErrorSpec
  -> ToErrorPresentation Mapping transforms the specification
  -> Build Mapping creates the complete finite table
  -> checked original application/Entry join
  -> original transport or protected saved-status projection
```

The Policy chooses an `ErrorSpec`. Its branches use declared Calculations, as required by the existing syntax. The Mapping is outside the Policy:

```alch
mapping ToErrorPresentation:
  input spec ErrorSpec
  target Presentation
  total true
  field coverage <- spec.coverage
  field code <- spec.code
  field message <- spec.message
  field category <- spec.category
  field httpStatus <- spec.httpStatus
```

`Build` composes them using the existing bounded collection operation:

```alch
field cases <- map([ContactUpdateRejection.PreferenceChanged],reason:ContactUpdateRejection => ErrorCase(reason=reason,presentation=ToErrorPresentation(spec=SelectErrorSpec(reason=reason))))
```

That line is a shortened illustration of the expression, not a complete valid CRM table: the actual source lists all twelve reasons. Its `Plan` invariants require twelve unique reasons. Ordinary record invariants also pair Conflict with409, Forbidden with403 and InvalidInput with422. The consumer additionally compares the table against the actual captured finite enum, so adding a new reason cannot silently leave it unmapped. The mandatory Policy `otherwise` returns `Unmapped`; reaching it fails table derivation.

`SpecifyError` constructs a value; `ToErrorPresentation` constructs another value. Neither sends HTTP, starts a retry or executes a provider call.

## Compile a real source selection

Use the matching rebuilt or installed Core/AlchLang pair. The frozen pre-feature CLI pair does not acquire this feature through a documentation change. The native CRM path also needs the matching installed `@craft/ai-profiles` package. Use absolute paths and fresh output directories.

From an installed consumer containing the CRM source under `reference-apps/crm`, set `CRM` to that absolute directory and `WORK` to an existing absolute writable directory. Package resolution for application generation begins from the source project, so keep the copied sources inside the prepared consumer.

```sh
alchlang profile check-source "$CRM/contracts/error-profile.json" \
  --source-root "$CRM"

alchlang profile compile-source "$CRM/contracts/error-profile.json" \
  --source-root "$CRM" \
  --out "$WORK/crm-error-selection"
```

The source envelope selects `craft.error-presentation/v1`, a genuine technical-profile-family Interface, the pure `Build` Mapping and an error contract identifying the original producer and reason type. The selection has no runtime request arguments, native resources or effect handlers.

The owner captures and hashes the full unchanged `journey.alch` file. For technical checking it derives only the exact declared nullary reason Enum into a staging type module, with original source span/hash and projection hash recorded in `source.reason_projection`. Business Operations, including `enforce`, do not thereby gain technical-profile execution admission. The compiled selection retains the complete original source file and rederives the projection on reopen. Actual application binding then compares the checked enum with the accepted application's enum and resolves actual Entries targeting the selected producer. A private Operation is not made public merely to import a type.

Compilation uses the existing bounded Core evaluator. It produces immutable checked rows, not runtime code that reevaluates business conditions. The original source owner enforces currentness and rejects altered source or compiled descriptors on reopen.

## Generate a protected application overlay

For a checked protected business application whose actual Entry targets the profile's declared producer, the existing CLI joins all three inputs together:

```sh
alchlang profile generate-source "$WORK/crm-error-selection/selection.json" \
  --business "$BUSINESS_ROOT/business.alch" \
  --business-profile "$BUSINESS_ROOT/contracts/selected-profile.json" \
  --http-profile "$BUSINESS_ROOT/contracts/http-profile.json" \
  --out "$WORK/presented-application"
```

`BUSINESS_ROOT` must be an existing compatible protected application root, not the raw CRM journey alone. Its actual Operation/enum/Entry must match this CRM selection; selecting an unrelated application fails. The raw journey plus its separately authored Entry access metadata are composed by the full CRM command below. Supplying a qualified name string or copying a same-looking enum is not a substitute for that original application join.

The overlay emits:

- `application.mjs`: public facade reopening the captured original application and source selection;
- `application/`: original generated application artifacts;
- `error-profile/selection.json` and its captured `sources/`;
- `error-table.json`: checked immutable table with source/version identity;
- system and business–system bridge views linking the selected presentation to the original producer/Entries;
- `error-application.json`: exact generated file identities.

The facade's original-owner methods prepare, review/accept, open runtime, bind rich HTTP or protected Entry HTTP, and assert currentness. Local build acceptance records a concrete checked source choice; it is not a new user prompt at every coding step and grants no application actor permission. Generated modules continue to use original runtime owners and actual operator-supplied resources.

## Generate the complete CRM backend

The opt-in project adds one source selection:

```json
{
  "errorPresentation": "contracts/error-profile.json"
}
```

This is an excerpt of `application-project-errors.json`. Run its public command from the matching installed consumer:

```sh
./node_modules/.bin/alchlang-generic generate-application \
  --project "$CRM/application-project-errors.json" \
  --out "$WORK/crm-with-errors" \
  --accept-local-review local-owner
```

The CLI derives the table from captured Alch source. An application intent cannot supply a handwritten error table and pretend it came from the source owner. In addition to the normal `source/`, `generated/`, bindings and origin records, the new project emits `error-api/` with the checked direct error API overlay. The API preserves the original permission checks and uses the selected table only for the original producer's Rejected result. Normal model/provider workflow wiring remains generated through the native application profile.

For a direct business rejection, the selected public response has the fixed form:

```json
{
  "kind": "error",
  "error": {
    "code": "preference-changed",
    "message": "Contact preferences changed. Review the latest preferences.",
    "category": "Conflict",
    "correlationId": "<server-issued opaque support token>",
    "presentationVersion": "<captured presentation digest>"
  }
}
```

The HTTP status is409 for this row. The two placeholder values above illustrate owner-generated metadata, not literal configuration values to copy. UInt64 values such as status are canonical decimal strings in the Alch computation wire format; the consumer validates the finite allowed values and converts them into HTTP numbers. It also uses the enum's actual wire code, for example `source-stale`, rather than assuming the source member name `SourceStale` is the API code.

A table is bound to the actual producer, Entry, enum and original `Rejected` outcome. A matching string in a different Operation, a `Failed` result, an Auth error or a provider response does not select a business row. Unknown or invalid presentation data takes a constant bounded internal-error fallback. Projection failure never reevaluates the Operation or repeats its effects.

## Keep asynchronous results separate

Submitting CRM work schedules the original workflow and retains the current scheduling response200. A business rejection or provider outcome produced later cannot rewrite that already-sent response.

The opt-in native profile persists diagnostic provenance from actual original invocation results and validated provider observations, then renders a safe public value through owner-filtered `ProfileStatus`/`ProfileStatusEntry`. The native workflow facade exposes the existing authorized read as `status(actor,{run,ordinal,attempt})`; it does not add an HTTP status route. For example, a caller can inspect the second CRM stage after it has a saved result:

```js
const result = await workflow.status(customerActor, {
  run: "101",
  ordinal: "2",
  attempt: "1"
});
```

`customerActor` is a genuine actor from the original Auth integration. A customer outside the stored owner scope receives no matching result. The public projection omits raw internal reason, provider receipt, source data and proposal bytes. A missing stage result stays missing: it does not prove completed, rejected or unknown. Suspended-unknown workflow state has its original recovery owner and is not exposed through a new public unknown-state endpoint by this feature.

The additional diagnostic schema is opt-in and uses new stores/namespace. Existing applications keep their old source/schema and stores. Reopening an incompatible old store under the new model must reject before commands/effects; there is no implicit migration, old-row decoding promise or journal rewrite. HTTP-only presentation does not by itself change entity storage shape. Use explicit original compatibility rules for durable command replay.

## Preserve platform and provider semantics

Auth, framing, routing, storage and execution faults retain fixed owner-controlled status/category mappings. A business table cannot turn AuthenticationRequired into success or convert upstream credential failure into a client login challenge. Unselected HTTP paths retain legacy envelopes/statuses; v1 opt-in supplies the fixed public envelope and distinguishes business rejection from internal failure.

Presentation is separately versioned and captured per generated application instance. Stored business outcomes remain immutable. Replaying through the same captured instance uses its table; an explicitly regenerated/versioned API may change presentation only while the original runtime's business/store/replay compatibility checks still permit it. No mutable response table changes an existing command's meaning.

Provider presentation starts from a validated original connector observation, not an arbitrary HTTP status/body. Confirmed, no-effect and unknown remain original dispatcher/connector meanings. Rate limits and provider authorization failures receive safe descriptions without adding retry authority. A lost acknowledgment or unknown write still requires original inspection; HTTP503 and a readable message do not permit another write or provider failover. Credential rotation, delays and retry budgets remain with their original owners.

## What is authored and what is generated

Business types, Rules, eligibility Policy, Operations and Entry permissions remain authored Alch. Public error code/message choices, categories and profile selections are also authored source/configuration. Craft evaluates these supported profiles and generates the table, exact original-owner joins, API overlay, optional saved-status model and lineage. Existing infrastructure implements the bounded evaluator, Auth, persistence, transport and provider adapters once; no CRM-specific JavaScript mapper is needed.

A bounded static message is not a secrecy theorem. The profile must use public-safe wording. Runtime provider bodies, exception messages, approval/source digests, customer identifiers and tokens cannot be interpolated into the finite source table. Correlation IDs are server-issued support tokens, not command identity, provider IDs or access grants. Semantic confidentiality of arbitrary author-written text and real provider/model qualification remain separate concerns.

## Open Questions

Current consumers are the selected Node HTTP boundaries, generated protected overlay and owner-filtered saved CRM status. Public pending/unknown workflow status endpoints, automatic migration of existing async stores, gRPC/event-specific renderers, localization, arbitrary provider raw-error parsing and externally exposed retry scheduling headers are not implemented by this feature. Local hosting, TDE, EVF, deployment and publication remain deferred. Focused fixture/source/native parity checks and the consolidated implementation proof do not qualify a real provider/account or measured model quality.
