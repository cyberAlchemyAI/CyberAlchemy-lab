# CRM requirements with profile-owned execution

A CRM enrichment proposal should update a verified contact only when preferences permit it, the proposed industry is supported by permitted evidence, and a person approved the change. This example expresses those business requirements directly. A contact's identity, evidence revision and preference version are business data: the rules actually use them. Transport clocks, source-owner revisions, release permission, destination identity, hashes and provider attempt state are not business inputs.

`journey.alch` contains the clean model input and proposal, meaningful approval decision, evidence, assignment calculations, typed eligibility policy, enforcing operation and result mapping. `entries.alch` keeps original permission beside the public Entry. `preferences.alch` retains the existing stored preference model and protected Query. `error-presentation.alch` maps the six authored business rejection reasons to safe public responses. No JavaScript application glue or simulator is included.

Select `Profiles.CrmDomainApplication@0.1.0` from the sibling `crm-domain-application.profile.json`. The explicit `crm-contact-enrichment/domain-v1` family supplies the technical projection/guard join; the old `crm-contact-enrichment/v1` family remains available unchanged. The same existing provider, inference, native implementation and architecture profiles are reused. The selected profile assembles original private source checks, approval mechanical binding, protected Entries, final payload disclosure and original dispatcher. A pure business decision never grants permission to call the provider.

## Generate

Use a matching tested local Core/AlchLang/native installation, with these example files copied into a fresh project containing the relevant packages. From that project directory:

```sh
mkdir profiles generated
node_modules/.bin/alchlang profile compile-source node_modules/@domainspec-v2/cli/examples/technical-profile-source/crm-domain-application.profile.json --source-root node_modules/@domainspec-v2/cli/examples/technical-profile-source --out profiles/crm-domain-inputs
node_modules/.bin/alchlang-generic generate-application --project application.json --out generated/crm --accept-local-review crm-domain-example-owner
```

These commands generate source and artifacts; they do not start a server or call a real provider. The environment file selects recorded local fixture identities. It contains no credentials or grant of deployment authority. Use a fresh application store/namespace for the new contract; existing legacy application stores are not migrated.

## What is generated and what people still supply

Profiles derive source projections and native/model/provider selections, append technical admission declarations and protected worker Entry, and generate the original API/runtime composition, system graph and business-system bridge. Domain rejection and technical rejection retain separate true producers while sharing public presentation machinery. The generated runtime uses the original source, model, workflow, Auth and effect owners.

A user still writes business requirements, domain concepts, desired Entry permissions and public wording; formal claims remain optional. An operator supplies actual source records, protected preference data, genuine approvals bound to the reviewed proposal, credentials, Auth grants, private stores and host resources. Those operational resources are not handwritten application code. Runtime/provider qualification is separate from local fixture success.

## Open Questions

The selected implementation and consolidated proof at `goals/plans/craft-domain-execution-separation-2026-11-01/` own current verification status. Full application admission/recovery negatives are separate from focused pure business-policy examples. Production Auth ingress, live provider/model qualification, hosting, TDE, EVF, deployment and publication remain deferred.
