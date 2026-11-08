# Generate an application from business sources and profiles

Craft checks domain models and relationships and generates implementations. AlchLang is the authoring language that supplies those models. A generation profile supplies supported technical choices: API routes, request limits, implementation layout and dependency wiring. You author business requirements, calculations, rules, mappings and public operation intents. Formal claims are optional and remain unproved unless a separate proof process establishes them.

## Install the prepared tools

The preview is distributed as two local CLI archives from the prepared GitHub repository envelope. It has not been published. With Node 26.8.1 on Linux x64, run from a fresh consumer directory:

```sh
npm init -y
npm install --ignore-scripts /absolute/path/domainspec-v2-cli-1.3.0.tgz /absolute/path/cyberalchemy-alchlang-0.7.0-candidate.0.tgz
```

AlchLang installs its pinned TypeScript 6.0.3 dependency. Node generation needs no Rust, Lean, database, message broker or local server. Keep the archives available for reproducible installation. Apache-2.0 terms and support at hello@cyberalchemize.com apply.

## Generate one business-only application first

Copy the bundled business-only inputs into the empty consumer root:

```sh
cp node_modules/@cyberalchemy/alchlang/examples/profile-engine/business-notice/* .
npx --no-install alchlang profile select project.json > selected.json
npx --no-install alchlang profile check project.json
npx --no-install alchlang profile plan project.json > plan.json
npx --no-install alchlang profile view project.json > views.json
npx --no-install alchlang profile generate project.json --out generated
npx --no-install alchlang profile verify project.json --out generated
node --input-type=module <<'JS'
import {handler} from './generated/app/index.mjs';
const response=await handler(new Request('https://example.invalid/receiveNotice',{
  method:'POST',headers:{'content-type':'application/json'},
  body:JSON.stringify({payload:{id:'7'}})
}));
console.log(response.status,await response.json());
JS
```

The v2 project selects one application model and public Mapping-to-Operation intent with zero function entries. The business manifest authors ontology meaning, accepted definitions, explicit exact-subject owner decisions, Rule/invariant/guard argument paths and the whole-input result. Bundled acceptance records are synthetic examples. Claims remain unproved; changing accepted meaning requires a matching new decision and invalidates the source lock.

The handler needs no caller-written native store: the profile supplies empty-effects settlement and returns {id:"7"} with the full committed outcome. This performs no persistence, event publication, external call or network listening. Use business-acknowledgement for an independent Entity/Boolean false-guard example with a retained label. Malformed fields reject before begin; false guard starts and rolls back without commit.

Select node-http-shared-ports-v2 for one actual typed transport consumed by the entries, or node-http-api-prefix-v2 for /api/ routes and api/index.mjs placement. Package-only extension is finite; unsupported new primitives/providers/guarantees need compiler qualification. The installed Craft package's docs/BUSINESS-APPLICATIONS.md contains complete blank-project files, digest calculation and explicit decision revision; docs/PROFILE-PACKAGES.md contains the exact custom-profile authoring recipe.

## Select a profile and generate the quote service

Copy the installed example into your own project:

```sh
cp -R node_modules/@domainspec-v2/cli/examples/profile-engine/quote-business ./quote-business
node --input-type=module - <<'JS'
import fs from 'node:fs';
import path from 'node:path';
const file='quote-business/project.json';
const project=JSON.parse(fs.readFileSync(file,'utf8'));
project.profiles[0].path=path.resolve('node_modules/@domainspec-v2/cli/profiles/node-http-entry-local-v1');
fs.writeFileSync(file,JSON.stringify(project,null,2)+'\n');
JS
npx --no-install alchlang profile select quote-business/project.json > profile-selection.json
npx --no-install alchlang profile check quote-business/project.json
npx --no-install alchlang profile plan quote-business/project.json > profile-plan.json
npx --no-install alchlang profile view quote-business/project.json > profile-views.json
npx --no-install alchlang profile generate quote-business/project.json --out generated-quote
npx --no-install alchlang profile verify quote-business/project.json --out generated-quote
```

`select` reports the complete source/profile/core/tool lock. To reuse it, write the `lock` member of profile-selection.json to a separate JSON file and pass `--lock path/to/lock.json`. A changed source, asset, compiler or tool rejects that old lock. `plan` prepares checked objects and reports intended artifacts; it does not run providers or write a final output. `generate` checks the complete native output and completes it into a fresh directory. An occupied destination is preserved. `verify` rebuilds the expected plan and compares the exact inventory and current inputs. Use a different output directory after changing your model.

The generated dispatcher is `generated-quote/app/index.mjs`. It exports `handler(Request, environment, io)`. No server starts. Hosting and deployment belong to a separate operational workflow.

## Expose an API and consume an external API

The business author explicitly declares `requestQuote` and `describeQuotePolicy` as public intents in project.json. The profile derives POST routes from those intent IDs. The first handler reads an inventory provider using GET, validates its exact wire schema, applies the stock rule and computes unit price times quantity using checked UInt64 arithmetic. It returns total_minor as an exact decimal string. Unavailable inventory returns the authored unavailable outcome and zero total.

provider.json identifies a read operation, a versioned wire schema and compatible field projection/renaming. It cannot compute prices, change units, grant permission, invent a write or reinterpret a provider failure as business success. The actual URL is an operator value. Secrets stay outside source files and generated artifacts.

Run without a server or real provider:

```js
import {handler} from './generated-quote/app/index.mjs';
const response=await handler(new Request('https://example.invalid/requestQuote',{
  method:'POST',headers:{'content-type':'application/json'},
  body:JSON.stringify({request_id:'Q1',sku:'S1',quantity:3})
}),{DEPENDENCY_INVENTORY_URL:'https://inventory.invalid/stock'},{
  fetch:async()=>Response.json({sku:'S1',stock:5,unit_price_minor:1250})
});
console.log(await response.json()); // total_minor is "3750"
```

At actual invocation, omitted injected fetch uses the runtime fetch implementation. Supply explicit destinations and selected credentials; generation itself never calls a provider. Input, response schema, status, byte-limit and deadline failures remain distinct.

## Change architecture without changing business behavior

Select `node-http-shared-ports-v1` by replacing the profile ID and directory in project.json. Its version remains 1.0.0. It creates a separate owned HTTP port module consumed by the entries. The entry-local profile uses entry-owned transport wiring. Both must preserve the same business results. Merely renaming directories is not an architecture qualification.

The appointment-business example demonstrates two independent external reads, boolean accessibility conditions, timestamps and an exact duration-times-rate-plus-venue-fee calculation. Its provider configuration also demonstrates field renaming. It performs eligibility inquiries; it creates no booking.

## Join an existing Craft application Operation

An optional application_calls entry names an existing application-v1 carrier, its Operation and an authored Mapping binding:

```json
{"id":"receiveNotice","source":"application/commerce.alch","operation_ref":"commerce:receive-notice","mapping_binding_ref":"message-mapping:consume-order","access":{"kind":"public"}}
```

Copy the installed `craft-application-source` example under your project as `application`, then add this record to project.json. The exact existing companion/evidence files are required. This compatibility carrier contains explicit technical runtime declarations; their derivation from business-only application sources is not claimed by this adapter. The profile-generated service entry uses the actual checked whole-application request handler and Operation export.

Supply `io.applications.receiveNotice` with a typed transactional store port. A request body `{"payload":{"id":"7"}}` passes through the authored Mapping. The value adapter preserves committed, rejected, failed and indeterminate outcomes, including stage, code, continuation and cleanup details. It never invents durability, retries or event publication. Missing ports reject before effects. Preflight cancellation is supported; required in-flight cancellation is rejected explicitly. No PostgreSQL, broker or other provider is started.

## Read the models and evidence

The business view connects source declarations and public intents to their obligations. The system view projects existing checked domain/application graphs and component dependencies. The bridge connects source selectors, profile rules, components and artifacts. Formal claims remain explicit residue. Linked, generated, checked, finite-case observed, proved and admitted states are distinct.

For the installed business-only project, `profile view` above writes the model views to `views.json`. Inspect that file beside `selected.json` and `plan.json`: the selection records the exact source/profile/tool lock; the plan names intended artifacts; the views show how authored business objects are connected to generated components. After generation, `profile verify` checks the output against those same inputs. Changing the selected profile or business source calls for a fresh output directory and verification run.

## Choose the path that matches your application

| Path | What you author | What the current installed tools do | Boundary |
| --- | --- | --- | --- |
| Business-only v2 profile | Business manifest, `.alch` declarations, public intents, selected profile and accepted meaning decisions | Generates an in-process `Request` handler and business/system/bridge views; the bundled notice example has zero effects | No durable store, broker, outbound write or listening server |
| Quote function profile | Quote business model, selected Node HTTP profile and external inventory read binding | Generates a public POST handler that calls an injected or runtime `fetch`, validates the inventory response, applies a stock Rule and checked UInt64 price calculation | This is a read and a calculation, not an order or booking write |
| Existing application compatibility entry | Complete existing application-v1 source, companion bindings, Mapping and Operation reference | Generates an entry that calls that checked Operation through a caller-supplied transactional port | The user supplies the application source, store port and operational realization |
The five-service Commerce source is an internal qualification case and is not
included in the installable archives. The bundled protected API example runs
its generated handler with isolated Auth fixtures. A production host must
supply its own credential verifier and credential-to-actor integration.

## Optional formal model export

Ordinary `profile generate` works without a FormalClaim. Claims can state additional domain or operation obligations, but generation does not prove them. The installed `alchlang-generic formal-export` command exports supported bounded Rules to SMT-LIB 2, checked Workflows to TLA+, and selected stateful Entry structures to Alloy. It emits a model and manifest for separate review; it runs no solver and provides no TDE or EVF verdict. The AlchLang package's `docs/GENERIC-APPLICATIONS.md` gives a claim-free installed Rule command, while `docs/FORMAL-CLAIMS.md` describes the optional claim contract. Its `docs/COMPUTATION.md` explains Mapping, filter, reduction, sorting and exact arithmetic separately from proof claims.

Optional ORODI profiles generate operational expectations only. They do not collect observations, export telemetry or grant runtime eligibility/admission. Local hosting, TDE, EVF and publication remain deferred.

## Open Questions

Unsupported source/ontology shapes, new primitives, new callable guarantees, persistence or messaging providers, recovery behavior and broader targets require separate adapters and qualification. The protected examples use fixture Auth; production use needs a credential verifier and credential-to-actor adapter. The tools do not generate every possible application or prove authored claims.
