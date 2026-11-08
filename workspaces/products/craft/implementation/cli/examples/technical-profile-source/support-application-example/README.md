# Reviewed support replies from business-only Alch

The business model permits a reply only for the correct customer, current ticket,
shareable and permitted evidence, independently reviewed content and an actual
business approval. It assigns priority and can select escalation. The send
operation rechecks eligibility and rejects an escalation instead of posting it.

`business.alch` contains those requirements using the existing types, rules,
calculations, mappings, typed policies and `enforce`. `entries.alch` keeps the
`ticket.reply` permission beside the entry. Source freshness, model correlation,
transport identities, provider attempts, clocks and mechanical approval/content
bindings are supplied and enforced by the selected profile and original owners.
Formal claims are optional.

Select `Profiles.SupportApplication@0.1.0` from the sibling
`support-application.profile.json`. In a project with the matching tested local
Core/AlchLang/native packages:

```sh
mkdir profiles generated
node_modules/.bin/alchlang profile compile-source node_modules/@domainspec-v2/cli/examples/technical-profile-source/support-application.profile.json --source-root node_modules/@domainspec-v2/cli/examples/technical-profile-source --out profiles/service-inputs
node_modules/.bin/alchlang-generic generate-application --project application.json --out generated/support --accept-local-review support-example-owner
```

The profile derives the existing model → RAG/content review → conditional Zendesk
reply recipe, source bindings, original-owner bootstrap, API handler, architecture,
system graph and business–system bridge. There is no authored application intent,
source-selection/stage-selection JSON or application-specific JavaScript here.
The library's technical templates reuse the original implementations and codecs.

An operator supplies genuine source records, approved candidate-bound review and
approval records, original Auth grants/private stores/model resources, the actual
source-gated generated RAG answer resource and the original Zendesk connector and
dispatch resources. A provider account is separate from the reply's customer.
The connector retains `safe_update`/`updated_stamp`; uncertain delivery requires
inspection of the original effect and never a blind resend.

`fixtures/business-cases.json` contains thirteen labelled business cases. Recorded
model/provider fixtures do not establish real-provider or semantic quality.
Generation starts no listener or background worker. Use fresh stores for the new
family; no legacy migration is implied.

## Open Questions

The selected design and consolidated proof in
`goals/plans/craft-service-profile-extensions-2026-11-02/` own current verification
and unresolved limits. Hosting, TDE, EVF, deployment, publication, production Auth
and live provider/model qualification remain deferred.
