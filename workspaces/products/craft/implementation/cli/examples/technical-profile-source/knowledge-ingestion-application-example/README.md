# Knowledge ingestion with business-only Alch

Choose Activate, Review, Quarantine or Tombstone from real parser/chunk observations and authored document intent. Source/profile owners enforce current document access, exact index generation and release; the business request contains no execution flags or provider state.

`business.alch` supplies domain values, rules, calculations, policies and the decision operation. `entries.alch` preserves the original entry permission. `fixtures/business-cases.json` is a labelled synthetic business corpus. A document's edition/version is meaningful evidence data; it is not assumed equal to another document's edition or to the facts-record revision.

Select `Profiles.KnowledgeIngestionApplication@0.1.0` from the sibling `knowledge-ingestion-application.profile.json`. The profile generates original source projections, selected knowledge stages, architecture, bootstrap, system graph and bridge. No application-intent, application-sources, stage-selection JSON or application-specific JavaScript is authored here. Formal claims are optional.

## Generate

In a fresh project with the matching tested local Core/AlchLang/native package installation, copy this example's files. Then run:

```sh
mkdir profiles generated
node_modules/.bin/alchlang profile compile-source node_modules/@domainspec-v2/cli/examples/technical-profile-source/knowledge-ingestion-application.profile.json --source-root node_modules/@domainspec-v2/cli/examples/technical-profile-source --out profiles/knowledge-inputs
node_modules/.bin/alchlang-generic generate-application --project application.json --out generated/knowledge-ingestion --accept-local-review knowledge-example-owner
```

These commands generate files; they start no server or provider call. `environment.identity.json` contains public resource identities and recorded local-fixture selection, never credentials, grants or authority flags. Both supported architecture layouts are selected through the source profile, not handwritten application wiring.

## Runtime resources

An operator supplies genuine original document/release, Auth, storage, embedding/index/scope resources and grants. RAG additionally requires an opaque reference obtained from the generated ingestion application, a genuine query embedding resource, selected inference resources and an independent trusted reviewer. The generated bootstrap assembles the original handler/workflow/model/cache joins; the application author supplies no handler Map or stage callbacks. Operational control records required by the source gateway do not add a human-approval requirement to this business model.

Shared resources remain caller-owned. Use new private application stores for the new family; no cross-version migration is implied. Recorded model responses are fixtures and do not establish real model/provider quality. A reviewer resource can provide bad labels; checked binding does not prove factual truth.

## Open Questions

The selected design and proof in `goals/plans/craft-knowledge-profile-extensions-2026-11-02/` own current verification and unresolved limitations. New-family administrative retirement generation, legacy-store migration, remote synchronization, alternate backends, provider/model-quality qualification, hosting, TDE, EVF, deployment and publication remain outside this milestone.
