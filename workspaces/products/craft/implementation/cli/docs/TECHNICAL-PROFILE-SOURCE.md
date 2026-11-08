# Write the business once, choose how it is assembled

A business model says what an application means: which records exist, what an Operation does, when a Rule is true, and who may use each Entry. A technical profile says how supported implementation pieces are assembled around that meaning. Changing from separate Entry modules to a shared service should not redefine an invoice, weaken a permission or replace the business calculation with handwritten code.

Craft keeps these responsibilities separate. Alch source supplies checked types, Rules, Calculations, Policies and Mappings. A small JSON envelope identifies that source, its selected Mapping and the exact original consumer/implementation basis. Craft checks the model through its existing Core, evaluates bounded pure selection and derives an artifact that the original generator understands. No new Profile MetaType or second expression evaluator is involved.

## Start with the local examples

The [local source catalog](../examples/technical-profile-sources.json) lists the working examples, inputs, consumer and limits. It is discovery data, not a hosted registry or proof of provider readiness.

| Example | Why choose it? | What compilation produces |
|---|---|---|
| [Entry-local functions](../examples/technical-profile-source/architecture-entry-local.profile.json) | Keep the existing transport wrapper beside each generated public function Entry. | An actual `craft.profile-package/v1` package and original template assets. |
| [Shared-port functions](../examples/technical-profile-source/architecture-shared.profile.json) | Give generated Entries one shared HTTP port component and real dependency imports. | A different actual v1 package using the original shared-port recipe. |
| [Protected Entry modules](../examples/technical-profile-source/protected-EntryModules.profile.json) | Generate original Entry bundles for a protected transaction application. | A checked source-selection artifact; the original protected application owner performs generation. |
| [Protected service assembly](../examples/technical-profile-source/protected-ServiceAssembly.profile.json) | Add the original service/application facade around those Entries, with corresponding graph/bridge structure. | A checked source-selection artifact targeting the original service artifact owner. |
| [Generic protected command](../examples/technical-profile-source/business-generic.profile.json) | Reuse one typed atomic-state command role across compatible business domains. | A source selection; the original business owner resolves exactly one compatible Entry. |
| [OAuth credential resource](../examples/technical-profile-source/oauth-credentials.profile.json) | Select the original durable credential implementation without embedding tokens. | A source selection for the original native installer, with operator configuration supplied separately. |
| [CRM provider Policy](../examples/technical-profile-source/crm-provider.profile.json) | Let checked source choose bounded actions over the original provider attempt. | A source selection for the original provider-stage owner and its five-action runtime Decision consumer. |

The first two are public zero-state-change function-service realizations. They do not become protected database applications by changing a label. The protected pair uses a distinct consumer and retains the actual Auth/SQLite/transaction owners. Source-selected Entry/service variants are tested against unchanged CaseDesk and Schedule business models; those tests do not qualify a real external provider.

## Understand one profile before running a command

In the [shared-port Alch source](../examples/technical-profile-source/architecture-shared.alch), `Options` contains the allowed request size. `RequestWithinBounds` expresses a Boolean limit. `Build` is a pure Mapping that returns the bounded role/dependency topology. Its `Node` and `Edge` records are ordinary Value Objects from the [source library](../examples/technical-profile-source/library.alch).

The sibling envelope supplies four things that source labels cannot establish on their own:

1. `sources`, `boundary` and `selection` identify the exact module closure, family Interface, Mapping and selection arguments.
2. `bindings` join topology roles/ports to checked business functions or original registered descriptor/recipe contracts.
3. `target` names the compatible consumer and exact original package basis. A v1 function package, a protected transaction profile and a service artifact selection have different contracts.
4. `limits`, contract assets and resource requirements make bounds and external needs explicit. A string does not mint a native resource, credential or permission.

The admitted v1 adapter preserves the original package's generic `emit from intents` expansion. The source topology selects supported role/dependency archetypes; it is not application-specific generated code. The same resulting package can therefore be selected for different supported checked function inputs and intent names/counts. An unsupported topology or role rejects instead of inserting a handwritten callback.

The [protected service source](../examples/technical-profile-source/protected-service.alch) demonstrates a smaller choice. One `Layout` Enum and one Mapping select `EntryModules` or `ServiceAssembly`. The business application remains a separately checked input. The profile does not guess which Entry to create or infer permissions from prose.

## Check and compile source

These commands belong to the current working AlchLang frontend with the matching rebuilt Craft peer. An older frozen/public CLI pair does not automatically acquire them. Use `alchlang profile --help` from the working build to confirm the surface.

From the repository root, the example manifests live under:

```text
craft/projects/domainspec-v2/impl/cli/examples/technical-profile-source/
```

For the installed Core example directory `<examples>` (normally `node_modules/@domainspec-v2/cli/examples/technical-profile-source`):

```sh
alchlang profile check-source <examples>/architecture-shared.profile.json \
  --source-root <examples>

alchlang profile compile-source <examples>/architecture-shared.profile.json \
  --source-root <examples> \
  --out <new-package-directory>
```

The default implementation root is the genuine loaded Craft compiler package root. The shipped architecture profiles select package-relative `profiles/...` bases, so their templates and original recipes resolve inside that installed package. An explicitly authored custom or legacy profile with a repository-relative basis must pass `--implementation-root <matching-root>`; resolution uses that exact root, with no path guessing or fallback search.

`check-source` uses the original parser, Core semantic checks and computation evaluator. It checks the selected Mapping, selection Rules, bounded values, source/currentness and target shape. It performs no provider calls and generates no running application.

For the function architecture consumer, `compile-source` writes a real `profile.json` plus its copied, hash-checked original assets. The generated package has a portable identity and the exact numeric package version admitted by v1. Its provenance retains the distinct authoring model identity/version, Mapping, topology, source hashes and original basis. Those versions are deliberately not assumed interchangeable.

For the protected service, business-role, runtime and composition consumers, the same command writes `selection.json` and the exact checked source closure beneath `sources/`. This is a source-selection artifact, not a fabricated v1 package or a deployed API. Reopening it through `createTechnicalProfileSourceOwner().prepareCompiled(selectionPath)` rechecks the original Core and descriptor/source identities.

Choose a new output directory. Generation does not overwrite an existing package directory or silently replace source history.

## Use the generated artifact

An existing supported function project selects the compiled package using its actual emitted identity, version and directory:

```json
{
  "profiles": [
    {
      "id": "<id from the generated profile.json>",
      "version": "<version from the generated profile.json>",
      "path": "<package directory relative to the project>"
    }
  ]
}
```

That is the `profiles` portion of an existing checked project, not a complete project file. Keep its business sources, public intents and explicit external-read configuration. Then use the existing `alchlang profile check`, `plan`, `generate` and `verify` commands. The original package loader, locks, composer, generators and output checks remain in charge.

A protected service source selection is consumed by `createTechnicalProfileServiceArchitectureOwner` together with its genuine source owner/handle and an accepted original protected application owner/handle. `emit` delegates either to original per-Entry generation or to the original service artifact owner. Its generated API modules retain the authored HTTP profile, Auth checks, SQLite transaction semantics and durable command replay. It also emits source-Mapping-linked system and business-system bridge views. A source selection cannot supply a fake application handle or grant access to an Entry.

The working CLI performs that protected join without application-specific host callbacks:

```sh
alchlang profile compile-source <examples>/protected-ServiceAssembly.profile.json \
  --source-root <examples> \
  --out <new-selection-directory>

alchlang profile generate-source <new-selection-directory>/selection.json \
  --business <checked-business-root>/business.alch \
  --business-profile <checked-business-root>/contracts/selected-profile.json \
  --http-profile <checked-business-root>/contracts/http-profile.json \
  --out <new-application-directory>
```

The business root is an existing supported checked protected application source closure, including its authored bounds and transaction contracts. The command reopens the compiled selection, checks the business source through the original owner and delegates generation. Its internal local-build acceptance record is not a user sign-off between tasks. It creates no listener, deploys nothing and calls no provider.

The generated protected application module imports the matching `@domainspec-v2/cli/generic` runtime peer. Make that exact current peer available in the consuming project's dependencies; a local development project can link the current checkout. Generation does not silently install or substitute a different runtime. The CLI-created transient checking workspace can be discarded: the emitted original bundle carries its model/profile closure and can be reopened with that matching peer and the separately provisioned Auth/store configuration.

## Keeping a command stable when a response is lost

Protected service generation also emits `command-client.mjs`. It uses the existing operator-supplied durable identity port (`prepare`, `inspect`, `observe`) implemented by `createCommandIdentityStore`; its declared compatibility contract is `craft.command-identity-store/v1`. The generated module imports Node built-ins only. It does not install a native package or create a database itself.

```js
import {createClient} from './command-client.mjs';

const client = createClient({
  identityStore, // existing private durable operator resource
  baseUrl: 'https://api.example.test',
  subject: 'operator-7',
  fetch: authorizedTransport
});
const prepared = client.prepare('CaseDesk.ResolveCaseEntry', {
  caseId: '7',
  proposed: {caseId: '7', resolutionCode: '42'}
}, {logicalCommand: 'resolution-review-42'});
const response = await client.send(prepared.command);
```

A send makes one transport call with the original base64url command-key header and redirects disabled. It never silently retries or switches endpoints. If the response is lost, inspect the prepared command and explicitly send the same handle again. After restarting the client/store, prepare the same logical command and input to recover the same allocation. If no logical command is supplied, a new UUID identifies a deliberate new intent; persist the returned `logicalCommand` when it must survive a restart.

The allocation fingerprint includes the original application/Entry/input contract and exact endpoint. Changed input, contract or destination cannot reuse that logical command by allocating another key. Expired unknowns remain inspectable and cannot silently acquire a replacement. Identity is scoped by original application, service/Entry, subject and tenant. Long service/Entry labels use a stable bounded digest; allocated keys and headers must satisfy the checked server limits, with no truncation or replacement allocation. These client labels do not authenticate a caller: original server Auth, permission checks and business rules remain authoritative.

Optional `entities` slots and persisted `children` occurrences return stable allocations for explicit use by the caller/agent. They never rewrite the business input. For example, CaseDesk's `caseId: '7'` references an existing case and must remain `7`; an allocated ID for another record does not replace it. Automatic allocation-to-business-field Mapping is outside this client producer's current scope.

## Reusable business and credential selections

The catalog's `generic-protected-command` example discovers exactly one typed atomic-state Operation Entry in an original protected application. The same compiled source can select commands in different domains. It does not guess by name: zero or multiple compatible Entries reject. The emitted source selection retains original permissions and is consumed by the original business-binding owner; it is not a second business evaluator.

The `crm-provider-policy` example adds a real runtime Policy to the original CRM provider-stage family. Its Mapping supplies the existing payload, receipt, stable logical identity and bounded retry configuration. The separately checked `PlanProvider` Policy consumes exactly `owner.observation.attempt`, supplied by the genuine original effect owner. Its five actions dispatch, wait, inspect the original effect, disclose a completed result or halt; they never select another provider. The same-owner handler map and source/declaration hashes are part of the actual provider capability identity. Credential and public evidence inputs are outside this finite consumer. The public Policy source is kept byte-equal to the shared qualified model by the catalog test. Operator account/credentials stay resources, not embedded source secrets.

The provider Policy is admitted for the original mutating provider-stage family. `readCurrent: true` is rejected by this family. A Backoff or Dispatch decision cannot increase the original attempt budget, shorten a required provider wait, extend the original deadline or repeat an uncertain write. The original effect owner enforces those boundaries even if an authored Policy selects an unsafe action.

The `oauth-credential-resource` example selects the captured original OAuth resource factory and its exact native ABI. Compile-source emits a reopenable selection, not a token or an activated credential service. The operator supplies the captured package, durable private storage/encryption key, account/grant, registration, endpoint and current authority when calling the native installer. The original credential owner performs refresh, recovery and revocation. Actual provider rotation behavior still needs separate qualification; source checking and a synthetic token response do not qualify a real account.

The OAuth example uses the standalone native installer. It does not declare a supported constructor link from an OAuth child into a CRM child. The operator may supply an existing compatible credential port as a resource; arbitrary source-defined native constructor graphs remain unsupported.

## Composing checked source profiles

The `craft.technical-profile-composition/v1` consumer receives genuine checked child source selections. The root names their authored identity and version; formation records the actual selected source closures and requires them to remain current. Duplicate registered identities reject. An identity/version string alone does not select or authenticate implementation bytes. The parent Mapping returns `nodes` and `edges`; each node names a declared `kind: profile` binding with `availability: compiled-source-profile`. That binding declares child exports and maps each required resource to `self.resources.<id>`. Child exports are checked against the actual original business Entry, HTTP generation owner or captured native contract. Matching strings alone do not realize a capability.

A composition root Mapping must return exactly `nodes` and `edges`. Extra root fields such as `providerStages` or an application intent are rejected, rather than silently ignored. Runtime bindings belong to their supported runtime child, not the root or a pure architecture/business profile. Generation-only architecture/business source targets also reject external resource requirements they cannot install; the original protected runtime still receives its Auth/store configuration through its existing API. Root resource requirements are supported only through explicit compatible child resource maps.

Generation produces a composition manifest and linked system/bridge views alongside separate original-consumer artifacts. A protected architecture child generates its actual Entry modules or service assembly; a business-role child resolves original typed/effect-compatible Entries; a native provider child carries the original provider-stage selection. They are not converted into a universal zero-effect package. The same compiled root and child selections can be reused across compatible business domains; an ambiguous business role fails rather than selecting by name.

This is a split-artifact consumer, not a universal application compiler. The checked root can join a protected layout, business-role selections and a compatible native/provider-stage child. The public catalog contains the individual source families; it does not include a ready-made root for every application or automatically derive an application intent from domain prose. A root requiring an unsupported child export, codec/effect, transport or constructor link fails.

`native-bootstrap.mjs` installs captured native factories using explicitly supplied operator resources. Provider-stage selections use the existing source gateway, workflow invocation, authorization fences, release service and durable effect dispatcher. Operators still provide credentials, account grants, fixture or real transports and journal paths. The bootstrap does not invent actor custody from user JSON or start a listener.

Native installation uses genuine captured package handles and the exact package/version/export/factory/ABI/operation contract. The emitted composition also locks native artifact bytes; different package contents under the same name/version are rejected. `native-bootstrap.mjs` consumes compatible operator resources, not caller-provided JSON objects pretending to be a checked owner or authorization frame.

This consumer admits dependency initialization edges and independent native/provider-stage installation. Message and Observation edges require a selected original transport consumer and are rejected here. Each composed native binding must have one selected node; constructor dependency edges are rejected. Expanded initialization graphs must stay within the declared root bounds and cannot contain dependency cycles. A provider-stage child may bind the finite original-provider Decision contract: Dispatch, Backoff, InspectOriginal, Finish and Halt. Its sole Attempt argument comes from the genuine original effect-owner frame, and every handler retains that same provider owner. Actual checked Policy/Calculation declarations and their calls appear in the system/bridge lineage. Public JSON cannot supply that authoritative Attempt. Message transport wiring, arbitrary native constructor graphs and other runtime decision bindings require their own original invocation consumers and are rejected here. A generated application can reuse the existing application-intent compiler and recorded inference fixtures; this does not mean the complete application intent or inference behavior was derived from the composition topology. Qualification records must say which part was generated and which existing intent/configuration was reused.

## Know what stays yours

Application authors supply business requirements, meaningful conditions/behavior, Entry permissions and the selected profile/configuration. Formal claims are optional; no claim is required merely to generate code. An ambiguous business-to-technical role assignment must be resolved explicitly; matching a function name or natural-language sentence is insufficient.

Technical authors supply reusable selection/topology source and choose admitted implementation contracts. An additional profile over existing roles does not require profile-specific compiler code. A genuinely new effect kind, protocol or provider capability still requires implementation through its original owner. A profile descriptor alone cannot implement OAuth rotation, a message broker or a new database.

Operators supply real accounts, resources, credential references, destinations and budgets. Secrets remain outside source/package files. Runtime owners enforce current authorization, effect identity, retries and recovery; a Policy result is a typed plan, not a transferable permission token.

## Interpreting results

Source checking, package formation, generated local execution and real-provider qualification are different results. A deterministic package or passing fixture cannot prove that a provider accepted a payment, that a token rotated safely or that a model met a quality target. The source catalog states the limited supported slice; the final selected implementation proof records exact source/tool/package inputs.

Performance is experimental, with no speed promise. Whole integration-fixture timings include generation, authorization, source validation and multiple workflow stages; they are not measurements of provider-call latency. Configure explicit bounded operation and inspection budgets for the selected workload. An expired inspection must retain an unknown outcome rather than authorize a replacement write. Currentness, authorization and deadline checks remain required even when they contribute substantial execution cost.

During development, use focused checks, keep the shared interface mutable through its owner, and continue independent branches when one functional dependency is unresolved. Source admission is executable compatibility checking, not a new developer approval. Batch registry bookkeeping and keep one consolidated proof at the end of the selected objective.

## Open Questions

- Additional consumers, native protocols and role contracts require their exact original-owner implementations and checks; these examples do not advertise universal profile/plugin support.
- Real-provider/account qualification, production credential/resource setup and model quality remain separate from the local examples.
- Local hosting, TDE, EVF, deployment and publication remain deferred. The frozen release is unchanged by adding these working-source examples.
