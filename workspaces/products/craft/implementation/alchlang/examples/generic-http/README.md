# Generate a protected API with persistent state

This example generates an injected HTTP handler from a business model and two
profile selections. The handler calls the declared Operation, commits its state
and command result to SQLite, and applies the declared HTTP response Mapping.
It starts no listener. Use the tested Linux x64 / Node 26.8.1 pair.

After installing both downloaded CLI archives into a new npm project:

```sh
cp -R node_modules/@cyberalchemy/alchlang/examples/generic-http/. .
npx --no-install alchlang-generic generate --source business.alch --profile contracts/selected-profile.json --http-profile contracts/http-profile.json --entry ReviewDesk.CommitRequestApprovalEntry --out generated --accept-local-review my-api > generation.json
node exercise.mjs
```

The business model extends the calculated decision with an Entity, protected
Query, atomic Operation and Entries. Permissions stay with each Entry.
The application profile selects SQLite transactions, hidden concurrency revisions,
command replay and Auth integration. The HTTP profile selects GET/POST routes,
request limits and response Mappings. The handler uses Node 26.8.1's standard Request/Response APIs; storage uses
`node:sqlite`; authentication uses the native component packaged with
`@domainspec-v2/cli` 1.3.0. Server/framework selection belongs to the separate
hosting work, which remains deferred.

The exercise checks that an unassociated request returns 401. Its isolated Auth
fixture then associates a principal with the generated handler and grants the
root Operation and child Query permissions. Approval returns HTTP 200 with
`{"approved":true,"id":"23","total":"20","state":"Approved"}`. Retrying
with the same command key returns the original result without a second commit.
GET `/api/requests/23` observes Approved; the authored business version stays 7,
while the generated hidden revision tracks the state change.

`x-craft-command-key` carries the base64url encoding of an application command
key. It identifies a retry; it grants no permission. Test association supplies
the original runtime-bound authentication. Headers alone do not create a user.

## What is generated and what is supplied

`business.alch` defines the business types, rules, calculations, mappings,
state proposal, storage lookup, transaction and entry permissions.
`contracts/selected-profile.json` chooses the application mechanisms;
`contracts/http-profile.json` chooses routes. The matching execution and
transaction bounds are explicit input files.

Generation emits the application module, HTTP adapter, storage description,
business graph, system graph, business-system bridge and manifest. Inspect
these together with `generation.json` to follow an Entry into its implementation.

`fixture-rows.json` is starting test data. `exercise.mjs` supplies test
credentials, an owned temporary store and standard Request objects; it contains
no business implementation. The `generic/testing` helpers are isolated fixture
APIs. A production host must supply its real Auth integration and resource
lifecycle. This example does not install a production identity provider or
host a public API. Local hosting remains deferred.

The driver prints its retained state directory and closes the resources it
opened. Run it again for a fresh isolated store. Regeneration requires a new
output directory; pass it as `node exercise.mjs generated-v2`.

## Open Questions

The complete cumulative application matrix and general runtime performance remain
under qualification. Local hosting, TDE, EVF and publication remain deferred.
