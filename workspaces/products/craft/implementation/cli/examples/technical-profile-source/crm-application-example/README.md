# Generate a CRM application from business source and a reusable profile

This is a source-generation example, using the current matching local Craft/AlchLang/native distribution. It contains business behavior, Entry permissions and public error wording. The selected reusable profile supplies technical source projections, provider mappings and existing implementation choices. No application intent/source/effect JSON or handwritten runtime simulator is included.

The business files are copies of the current reference CRM model: journey.alch defines decision behavior, preferences.alch defines stored preferences and protected Queries, entries.alch keeps permissions beside the public Entry, and error-presentation.alch selects public messages. The small error-profile manifest selects that existing source error consumer; it does not contain executable rejection logic or a raw-provider mapper.

## Generate with an installed matching distribution

Start in a project directory containing node_modules with the tested Core1.3.0, AlchLang0.7.0-candidate.0 and native0.1.0 packages and their matching dependencies. This does not instruct installation from an unpublished package registry or start a host. Use a new crm-demo directory:

```sh
cp -R node_modules/@domainspec-v2/cli/examples/technical-profile-source/crm-application-example crm-demo
cd crm-demo
mkdir profiles generated
../node_modules/.bin/alchlang profile check-source ../node_modules/@domainspec-v2/cli/examples/technical-profile-source/crm-application.profile.json --source-root ../node_modules/@domainspec-v2/cli/examples/technical-profile-source
../node_modules/.bin/alchlang profile compile-source ../node_modules/@domainspec-v2/cli/examples/technical-profile-source/crm-application.profile.json --source-root ../node_modules/@domainspec-v2/cli/examples/technical-profile-source --out profiles/crm-inputs
../node_modules/.bin/alchlang-generic generate-application --project application.json --out generated/crm --accept-local-review crm-example-owner
```

The selected profile is Profiles.CrmApplication@0.1.0. The version and compiled selection path match application.json. Profile compilation captures its checked contract/provider/composition/layout source closure. Both output directories must be new; the parent directories are created explicitly above.

The environment uses the same recorded fixture selection as the local integration cases. Its model name is a fixture identifier here, not a model recommendation or evidence of a live call. Generation checks and emits source; it never calls OpenAI or HubSpot. Account77 and recipient5 are public synthetic identities, not credentials. Keep real tokens, keys and native Auth sources outside these files.

## What to inspect

- generated/crm/derived-application-inputs.json: source/intent/provider selections derived through the checked reusable profile.
- generated/crm/profile-inputs.json: bounded generated metadata, actual source/native identities and selected layout runtime entrypoint.
- generated/crm/profile-composition/native-bootstrap.mjs: the original generated native installer.
- generated/crm/application-bootstrap.mjs: the small caller that supplies missing inputs to original source/model/provider/Workflow owners.
- generated/crm/architecture/: actual selected layout artifacts; Workflow execution remains with createApplicationWorkflow, and the service facade is not advertised as independently complete.
- generated/crm/error-api/: the optional source-derived public error overlay selected by this example.
- generated/crm/profile-input-system-graph.json and profile-input-business-system-bridge.json: generated input/owner lineage alongside the original graphs.

A host must separately provide genuine native Auth/actor resources, source records and approvals, model/CRM transports and credentials, and private stores/journals. Opening the generated module starts no listener or background worker; advance is explicit. The host does not construct application gateways, stages or actor/handler maps.

For the full resource shape, identity checks, modes and approval read, see [APPLICATION-INPUT-PROFILES.md](../../../docs/APPLICATION-INPUT-PROFILES.md) in the Core package and the native application README. Application-store mode and Workflow journal mode can be explicitly different after partial startup; no existing store/history is deleted or silently reset.

## Open Questions

Production identity ingress, real provider/model qualification, source synchronization, hosting, TDE, EVF, deployment and publication remain deferred. The matching implementation report owns the exact source/build/installed evidence. This example is not a production service activation claim.
