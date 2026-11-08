# From business requirements to a CRM application

A CRM update is more than an HTTP request. It needs a business decision, the records supporting that decision, current permission and preference information, an approval for the exact change, and a way to preserve the original intent if the provider's response is lost. The application-input profile connects those meanings to the implementations Craft already has.

The business author describes what an update means and when it is allowed. A reusable profile supplies the technical translations once. The operator supplies real resources and identities. The application does not need its own JavaScript connector construction, source-projection JSON, worker actor map or workflow-handler map.

This working-source feature is a finite CRM family over the existing protected application owners. Formal claims remain optional. It is not a promise that arbitrary business prose, a new provider or a new native ABI can become an application without a corresponding supported contract. The frozen release does not acquire this behavior until its separately selected source/package pair is rebuilt and verified.

## Start with the business meaning

For a new business-only model, use [the complete domain CRM example](../examples/technical-profile-source/crm-domain-application-example/README.md) and select [Profiles.CrmDomainApplication](../examples/technical-profile-source/crm-domain-application.profile.json). Its `crm-contact-enrichment/domain-v1` contract keeps consent, duplicate detection, evidence grounding, assignment and `approval.approved` in authored business policies. Its authored request, model input, proposal and approval contain no compulsory `sourceCurrent`, `releaseAllowed`, execution `attempt`, transport recipient, hashes or clock.

The profile generates a separate private typed policy and protected operation that check actual source/release observations, immutable proposal origin and approval bindings/expiry. The original business operation receives only the clean projection. Technical admission runs again after business acceptance; the original dispatcher and release owners still decide whether an actual effect is allowed. A pure policy result never grants effect authority. Existing unknown or confirmed attempts are inspected through their original provider before any new admission or send.

Both technical and business denials have their own original producer and typed public presentation. Saved candidates retain the source/input/receipt identity captured when they were produced; a restart cannot relabel an old candidate with a newer source. New domain artifacts need their own compatible instance/store. This feature does not migrate an old application store or remove technical checks from legacy models.

The original `crm-contact-enrichment/v1` example below remains supported for existing projects; it includes the earlier combined request. Do not copy those technical fields into a new domain-only model.

The supported example prepares a contact update from permitted company evidence. It checks whether the proposal still describes the current contact, whether current preferences allow the update, whether its evidence supports the proposed enrichment, and whether the approval covers the exact source, destination and output. Business Rules, Calculations, Mappings and typed Policies continue to express these decisions. The Operation uses the existing `enforce` behavior; Entry permissions remain beside the Entry.

The input profile does not replace any of these decisions with a technical default. It selects the existing Operation Entry and preference Query by exact semantic roles. A business Mapping may be needed when a domain uses genuinely different meanings; copying provider field names into every application is not required.

The Entry and its target can belong to different modules. For example, `CrmOperationsAccess.PrepareContactUpdateEntry` targets `CrmOperations.PrepareContactUpdate`. Its `ReviewRequest` and `Decision` types belong to the target module. The profile resolves that relationship rather than deriving it from the Entry's name or from a similar-looking record.

## Understand the three inputs

| Input | Who supplies it | Why it is needed |
|---|---|---|
| Business model and semantic role assignments | Application author | State records, source relationships, decision behavior and permissions. |
| Checked application-input profile | Reusable profile library | Translate the supported role family into the existing source, application, provider and layout contracts. |
| Environment identity and runtime resources | Operator or generic host | Select the account, destination, model, budgets, credentials, native Auth resources, journals and stores for this instance. |

The [CRM profile source](../examples/technical-profile-source/crm-application.alch) uses the existing Value Object, Enum and Mapping meta types. `BuildInputs` returns bounded `ApplicationInputs`, including source roles, declared business type roles, an existing layout and the existing CRM provider profile reference. The [source envelope](../examples/technical-profile-source/crm-application.profile.json) selects `craft.application-inputs/v1`. The [contract asset](../examples/technical-profile-source/contracts/application-inputs.json) records the supported original consumers and nominal relationships. There is no additional expression evaluator or Profile meta type.

The library also reuses the existing CRM provider Mapping/Policy and original protected layout profiles. Their actual captured source and native package bytes stay part of formation identity. A descriptor alone cannot implement another connector or change the original retry rules.

## Separate business sources from generated technical inputs

The first profile uses existing document authority for facts, evidence and approvals, and the protected preference Query for current preferences. The operator/business workflows supply those records. A generated binding does not manufacture evidence or approve an action.

The preference Query's opaque observation revision is a SHA256 identity used for source currentness. `ContactPreferenceSnapshot.version` is a UInt64 business version. The generated source view exposes one matching record, so the business condition reads `record.allowed` and `record.version` from the same observation. The expected preference version stays the version captured by the business intent; it is not overwritten to make the comparison pass.

That source choice is explicit. The older example reads `contactAllowed` from facts. Selecting the new preference-Query profile is not a claim that those two business contracts are identical. The legacy source mode remains available.

The existing gateway needs facts and an approval control record even during the proposal stage. The approval source is nondisclosed and may initially record an unapproved state; a matching real approval is still required before effects. Preference reading can wait until the later stage. Model-input projections may read only the explicitly disclosed source roles and permitted input fields. Approval, private preference controls and owner/principal fields cannot be smuggled into the model prompt by changing a projection path.

## Choose the profile and keep source roles clear

The project identifies the business root and classifies its additional sources:

- Same-module domain additions go to the existing application's additional-source consumer.
- Entry access modules stay with the original authored Entry selection.
- Error-presentation source stays with the existing typed error consumer.

A different module must not be concatenated into same-module business additions. An exact business role assignment tells Craft which Entry/Query has the intended meaning; zero, ambiguous or nominally incompatible roles fail rather than guessing by field names. Concrete codec fingerprints are derived from the selected checked business instance, so a reusable library does not hardcode a hash of one application's complete model.

A source-input project using the shipped `Profiles.CrmApplication@0.1.0` selection has this shape. These paths name your business files and a previously compiled selection; the source-selection command below creates the latter. Optional `errorPresentation` can select the existing error-source manifest when the business defines custom public error wording.

```json
{
  "schema": "craft.application-generation-project/v1",
  "businessSource": "requirements.alch",
  "applicationProfile": {
    "id": "Profiles.CrmApplication",
    "version": "0.1.0",
    "selection": "profiles/crm-inputs/selection.json"
  },
  "businessRoles": {
    "decision": "CrmOperationsAccess.PrepareContactUpdateEntry",
    "preference": "CrmOperations.ReadContactPreferenceEntry"
  },
  "businessComponents": {
    "sameModule": ["preferences.alch"],
    "entryAccess": ["entries.alch"],
    "presentation": []
  },
  "environmentIdentity": "environment.identity.json"
}
```

`applicationProfile.selection` accepts a compiled `selection.json`, not an unchecked source manifest. This path uses the matching installed `@craft/ai-profiles@0.1.0` package. The original authored-profile project syntax remains an alternative.

With the matching working CLI, the ordinary source-profile commands still check and compile the selection:

```sh
alchlang profile check-source <core-examples>/crm-application.profile.json --source-root <core-examples>
alchlang profile compile-source <core-examples>/crm-application.profile.json --source-root <core-examples> --out profiles/crm-inputs
```

`<core-examples>` is the installed Core `examples/technical-profile-source` directory. Create the parent `profiles` directory before compilation, and `generated` before the application command below; the CLI owns each new final output directory rather than inventing its missing parents. Compilation captures the actual contract, provider composition, layout and source assets needed to reopen the selection; it is not a runtime activation or provider call. `profiles/crm-inputs` must be a new output directory.

Application generation retains the existing command name:

```sh
alchlang-generic generate-application --project application.json --out generated/crm --accept-local-review local-owner
```

The selected source-input implementation derives the configuration that the older authored-project mode supplies explicitly. Its project schema and packaged public exports must come from the matching working pair. Do not use an older frozen CLI with a newer compiled source selection. Exact project fields and the generated consumer are exercised by the selected implementation proof; old authored-project mode remains supported.

## Try the complete shipped source project

The [CRM application example](../examples/technical-profile-source/crm-application-example/README.md) includes the actual business model, preference Queries, Entry permissions, error policy and existing error-source selection. Its `application.json` and public fixture environment match the current source CLI schema. It does not include handwritten application-source/intent/effect JSON or a simulator. From a project directory containing the matching installed distribution:

```sh
cp -R node_modules/@domainspec-v2/cli/examples/technical-profile-source/crm-application-example crm-demo
cd crm-demo
mkdir profiles generated
../node_modules/.bin/alchlang profile check-source ../node_modules/@domainspec-v2/cli/examples/technical-profile-source/crm-application.profile.json --source-root ../node_modules/@domainspec-v2/cli/examples/technical-profile-source
../node_modules/.bin/alchlang profile compile-source ../node_modules/@domainspec-v2/cli/examples/technical-profile-source/crm-application.profile.json --source-root ../node_modules/@domainspec-v2/cli/examples/technical-profile-source --out profiles/crm-inputs
../node_modules/.bin/alchlang-generic generate-application --project application.json --out generated/crm --accept-local-review crm-example-owner
```

These commands check and generate without contacting a provider or starting a listener. The model/account values are explicitly recorded fixture choices, not live provider qualification or model recommendations. The source project selects custom error presentation; omitting that optional selection retains the original legacy public behavior. Use a fresh `crm-demo` and output directories rather than overwriting prior source/history.

## What is generated, and what is reused

Generation records those derived inputs in `derived-application-inputs.json`, preserves the compiled selection under `profile-input-selection`, and emits `profile-inputs.json` plus the original `profile-composition/native-bootstrap.mjs`. It also produces the current application intent/source/profile inputs, original business mirror and application/API artifacts, original provider selections, source-derived public errors when selected, source/native identity metadata and linked system/bridge views. It retains the existing `native-bootstrap.mjs` and adds a small `application-bootstrap.mjs` caller.

That caller does three central things through existing APIs:

1. Calls the original `native-bootstrap.install` to install captured native/provider resources.
2. Supplies genuine application access and the generated-descriptor gateway to the installation's `createProviderStages`.
3. Supplies generated worker actor assignments and stage handlers to the original `createApplicationWorkflow`.

The selected layout is used by the owned runtime: `profile-inputs.json` identifies its actual Start Entry artifact in `architecture.runtimeApplication`. For a Workflow application, the original ServiceAssembly facade deliberately remains incomplete on its own; its manifest names the existing `createApplicationWorkflow` execution owner and records `service_facade_complete_application: false`. A command client is emitted only when a real original HTTP profile exists; otherwise `command_client` is null and the original workflow submission port remains in use. This explicit join does not synthesize an HTTP contract or silently skip the selected layout. The original application owner still opens the protected runtime; the original Query/release/model/effect owners still enforce their checks. The generated caller does not implement another installer, Auth/session system, workflow engine, retry loop or HTTP protocol. Source origins and the system/bridge views show which business selector and profile Mapping produced each new input and how it reaches the existing owner.

## Run through an existing host, without hosting

The generated application bootstrap opens with explicit `create` or `reopen` mode and low-level resources supplied by the existing host. The corresponding native API is `openGeneratedApplication({directory, resources, mode, expectedMetadataSha256})`. The generated wrapper supplies the pinned metadata digest; callers normally import its `open` function rather than construct that digest themselves. It reopens the pinned generated artifacts, checks the selected native package bytes and preserves the existing application/store identity.

Resources include the original Auth/native source and actor issuer, document/release ports, selected model client/resource and exposure configuration, provider credential/transport resources, journals and store paths. Model configuration supplies `model.identity` equal to the selected nonsecret environment inference record, and the supported SDK/client exposes a matching `baseURL`; omitting those identity fields is rejected. These are configuration checks, not proof of a real provider's behavior. A host may lend an already prepared genuine runtime; otherwise the original runtime owner opens it. A host-supplied customer actor is authentication input, not application-specific wiring. The generated code creates the application's worker/handler maps rather than asking the operator to write them.

The host supplies named resources rather than application constructors:

| Resource | Actual contract |
|---|---|
| `artifacts` | Map keyed by the selected native package name/version, containing an original captured package artifact. |
| `nativeAuth`, `actorIssuer`, `workerSubject`, `customerSubject` | Original host native Auth and its `actor(runtime, subject, entry)` issuer; generated code builds the per-Entry worker map. |
| `storePath`, `journal` | Existing private state parent, application database path, Workflow journal directory and explicit create/reopen settings. |
| `documents`, `release` | Original document port (or its owner wrapper) and source-release owner; source records/approval decisions are populated separately. |
| `nativeResources` | Map from the generated provider resource ID to original connector account/credentials/HTTP, durable dispatch path/policy and the same release owner. |
| `model` | Selected SDK/client, complete original resource configuration, matching public `identity`, effect path and exposure path/allocations; no per-app controller callback. |
| `composition` + `handle`, `runtime` | Optional genuine borrowed owner/handle/runtime for the same generated business closure; omitted resources are reopened by their original owners. |

`mode` selects the original application-store mode. `journal.mode` defaults to it but can be explicitly different after a partial startup—for example, store `reopen` with journal `create` when the store was created before a later startup failure. The existing private journal parent must already exist. Local acceptance notes live in that parent; only the original Workflow driver creates its journal directory with its required private mode. The join never deletes/resets a preserved store, silently guesses a mode or pre-creates the Workflow directory.

The returned `approvalBinding(actor, {id, run})` is a read-only delegation to the original source gateway. An authorized approval workflow can use its exact source/input/manifest binding to create a real approval record. It neither approves that record nor bypasses business approval checks. The generated application also exposes its actual `runtime`, original `access` adapter and an `actor(subject, entry)` delegation for an existing host.

The returned application delegates the existing `submit(request, actor)`, `advance()`, protected `status(actor, key)` and `close()` behavior. Opening it starts no listener or background worker. Calling `advance` is explicit. Borrowed host resources remain borrowed; generated integration releases only resources it acquires through the original cleanup APIs.

Nonsecret account, recipient, model/destination/revision and budgets are selected before the original capability identity is formed. Runtime resources must match that selection. A different account or model requires a new generated selection; it cannot silently substitute itself under the old identity. Credentials may rotate through their existing owner within the selected account/grant family.

The environment's `effect.deadline_ms` selects the Workflow stage budget and the deadline of a newly prepared mutation. The original dispatcher limits a normal call to the smaller of its `timeoutMs` and the attempt's remaining deadline; a larger operator timeout cannot extend that mutation deadline. Recovery inspection is a different lifecycle: the original owner may open a fresh, separately bounded `inspectionTimeoutMs` window for the same uncertain attempt, including after its original mutation deadline. That operator resource setting is not part of the generated capability identity, and the Workflow stage timeout does not promise the remote operation was cancelled or reconciled. No additional timeout policy or dispatcher is introduced by the generated join.

If an update's acknowledgement is lost, the original effect remains unknown until its owner inspects/reconciles it. The generated join does not switch providers or repeat that write. Business admission's `Prepared` value is a separate phase from the provider dispatcher's attempt state. Direct coverage of all typed business errors does not mean every reason arises naturally in every running workflow.

## Know the verification boundary

Focused checks cover the changed generation, role, Query and integration behavior during development. The selected objective ends with one consolidated source/build/installed proof, including clean relocation, positive workflow execution, stale/foreign/tampered resources, original uncertainty/recovery and legacy compatibility. Generated metadata and a successful source check do not qualify a real provider, a model's quality or production identity ingress.

The inspected Auth host path is locally qualified against genuine sealed native-source fixtures. Generated runtime code does not import test helpers or accept actor-shaped JSON, and that local result is not advertised as production login/session support. Experimental timings carry no speed promise.

## Open Questions

A new unsupported host/Auth ingress, source synchronization service, provider ABI, transport or data migration needs its separately scoped original-owner implementation. Real accounts, approval production, provider/model qualification, hosting, TDE, EVF, deployment and publication remain deferred. The selected final implementation report owns exact tested package/source identities and any unrun facets; this guide does not substitute for that evidence.
## Knowledge ingestion and permissioned RAG

The source catalog also supplies `Profiles.KnowledgeIngestionApplication@0.1.0`
and `Profiles.PermissionedRagApplication@0.1.0`. These use the same checked
`craft.application-inputs/v1` consumer as CRM, with explicit finite knowledge
families. Their only application business role is the original protected decision
Entry. They do not require a contact-preference Query or CRM provider.

The ingestion profile selects the original prepare/activate index stages. The
business model decides Activate, Review, Quarantine or Tombstone from actual
parser/index observations and authored document intent. No paid text-model stage
is introduced; embeddings retain their original model accounting and source
disclosure owners. The original `CanActivate(Decision) -> Bool` Rule remains the
business continuation gate.

The RAG profile selects the original proposal/validation/release stages. It
requires an opaque original generated-ingestion reference, matching representation
and query embeddings, and a selected independent review resource. Citation and
refusal rules remain business Alch. Actual source access, full-context release,
generation identity, candidate provenance and cache disclosure remain original
runtime checks. Valid citations do not by themselves establish a true answer;
trusted reviewer configuration and real model quality remain separate concerns.

Both profiles bind parser/retrieval/reviewer observations only to corresponding
original producer paths. A profile cannot replace `parsed` or `answerSupported`
with a literal `true`, model output or similarly named field from an ordinary
facts record. Credentials, Auth grants, actual records and compatible resources
remain operator inputs. A business author writes no handler Map or application
stage-wiring JavaScript.

Examples are `examples/technical-profile-source/knowledge-ingestion-application-example/`
and `examples/technical-profile-source/permissioned-rag-application-example/`.
Select the matching sibling `.profile.json` and compile it through the ordinary
source-profile command, then select it in `application.json` as with CRM.
`EntryModules` and `ServiceAssembly` are explicit original architecture choices.
Use fresh stores for these contracts; no automatic legacy migration is provided.

The existing administrative retirement workflow remains supported through its
explicit legacy project. Regeneration of that separate workflow from these new
source profiles is outside this first knowledge milestone. Current source,
generated-runtime and installed results are owned by the consolidated proof for
`goals/plans/craft-knowledge-profile-extensions-2026-11-02/`; source admission does
not qualify a provider, model, issuer or deployment.

## Support, invoices and marketing

These source profiles extend the same generation path. They select existing
runtime owners; they do not require application-specific JavaScript handlers.

| Select | Business author supplies | Generated/runtime behavior |
|---|---|---|
| `Profiles.SupportApplication` | Ticket reply eligibility, escalation rules, `PrepareReply`, `AuthorizeReplySend`, `CanSendReply`, protected Entry | Grounded proposal using a genuine generated RAG answer; independent current content review; approved Zendesk reply to the actual ticket customer |
| `Profiles.InvoiceApplication` | Invoice reconciliation mappings/calculations, typed approval policy, `PrepareDraftPosting`, protected Entry | Original PDF/text parser and model proposal; current supplier/PO/receipts joins; exact approved amount/currency; Xero DRAFT posting within the current dispatch window |
| `Profiles.MarketingApplication` | Audience and preference rules, `PrepareDraft`, `PrepareSchedule`, `ObserveMetrics`, protected Entry | Original protected grouped preference Query; Mailchimp draft creation, content update, approved future schedule and read-only metrics as separate effects |

The sibling `support-application-example/`, `invoice-application-example/` and
`marketing-application-example/` directories contain complete business source,
Entry permissions, profile project selection, environment identities and fixture
inputs. Publish the matching checked `.profile.json` with the ordinary source
profile command, then run `generate-application --project application.json --out
NEW_DIRECTORY --accept-local-review OWNER`. Output includes the protected
application/Workflow, selected original architecture, `application-bootstrap.mjs`,
source inputs, system graph and business-system bridge. `open` accepts trusted
operator resources. No per-application handler maps or source binding callbacks
are needed.

The model candidate retains the original confirmed attempt, actual paid input,
original approval revision and disclosed dependency digest. Updating a private
approval or content review after the proposal is legitimate; it does not recreate
or restamp the model origin. Current source/disclosure/identity checks remain
private to the original technical owners. Business approval is projected from the
actual approval record. Support review/reply, invoice draft posting and campaign
scheduling enforce approval; campaign draft/content preparation does not require
it. Unknown external outcomes keep original inspect-first/reconciliation behavior
and cannot be retried through a different provider.

Operators still configure source documents, genuine reference/query resources,
accounts, credentials, permissions, model/exposure resources, compatible stores
and provider dispatch resources. The invoice profile creates drafts, not payments;
marketing scheduling acceptance is not evidence of delivery. Recorded SDK/model
responses qualify local fixtures only. Fresh stores are required; there is no
automatic legacy migration. Exact selected installed evidence is in
`goals/plans/craft-service-profile-extensions-2026-11-02/`.

### Open Questions

Real-provider setup and qualification, model quality, local hosting, TDE, EVF,
deployment and publication remain deferred. Further providers and arbitrary
profile synthesis are separate extensions, not implicit in these three recipes.

## Connecting generated applications

A system project selects independent business applications and a checked source
composition. Each application keeps its own protected entries, state, workflow
and runtime owner. The composition connects a consumer requirement to the
producer's original read contract. It does not copy business records, transfer
permissions or run jobs automatically.

The `connected-operations-example` selects six existing profiles and declares
three connections: ingestion supplies an active index to RAG; RAG supplies a
released answer to support; CRM supplies current grouped contact preferences to
marketing. Invoice processing runs independently. A marketing connection requires
an actual authored CRM preference Query with `contactId`, `email`, `version`,
`allowed` and `identityVerified`; the compiler checks its original field types.
A family name alone cannot establish this compatibility.

After compiling the source selections, generate the complete system:

```sh
alchlang-generic generate-application-system \
  --project system-project.json --out generated \
  --accept-local-review local-owner
```

The existing application generator generates each child. `application-system.json`
records its exact artifacts and checked connections; `system-bootstrap.mjs` opens
them through the original runtime owners. `system-graph.json` references the
actual child graphs by path and hash, and `business-system-bridge.json` preserves
the original child bridges with application-qualified references. These are
source-generation views; runtime execution has separate evidence.

The operator supplies `resources.applications` (a Map from alias to each child's
original infrastructure resources), `resources.joins` (a Map keyed by
`consumerAlias.port`) and the original native `resources.artifacts` Map. A
knowledge connection selects the exact completed producer `{id, run}`. A CRM
connection supplies bounded grouped Query inputs. The system derives the
reference, answer binding or Query lease; supplying a second manual resource for
the same slot rejects. Each producer checks its original actor and currentness.

Opening the system does not start a job. Call `system.open(alias)` when the
producer's prerequisite work is ready; unrelated applications can proceed while
another dependency is pending. Users still submit business work and approvals.
Closing and reopening application stores requires reacquiring process-local
references and Query leases from their original owners. This is not a promise
of a distributed transaction, automatic source migration or process-crash
recovery of every external resource.

### Open Questions

Executed layouts and recovery cases are owned by the connected-application plan
and its final proof. Arbitrary application contracts, general Query multiplexing,
real-provider/model qualification and deployment remain outside this finite
connection set. Hosting, TDE, EVF and publication remain deferred.
