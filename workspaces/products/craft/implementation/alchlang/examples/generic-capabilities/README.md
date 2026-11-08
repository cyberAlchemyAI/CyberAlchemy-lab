# Checked capability selection through the source CLI

This example reuses the existing bounded-values profile, business value types,
Interface grammar and pure Operation generation. `selection.json` extends that
path with an explicit neutral inference contract. It binds exact authored
source/profile bytes and the existing integration kernel. The fixture package
identity describes the selected realization; it is not installed or executed.

From the frontend directory, use the selected source Core package and Node runtime:

```sh
ALCHLANG_DOMAINSPEC_PACKAGE_ROOT=/absolute/path/to/craft/projects/domainspec-v2/impl/cli \
node --import tsx src/generic-composition-cli.ts inspect \
  --source examples/generic-capabilities/business.alch \
  --profile examples/generic-capabilities/profile.json \
  --capability-selection examples/generic-capabilities/selection.json

ALCHLANG_DOMAINSPEC_PACKAGE_ROOT=/absolute/path/to/craft/projects/domainspec-v2/impl/cli \
node --import tsx src/generic-composition-cli.ts generate \
  --source examples/generic-capabilities/business.alch \
  --profile examples/generic-capabilities/profile.json \
  --capability-selection examples/generic-capabilities/selection.json \
  --operation Example.Answer --out /absolute/new/output \
  --accept-local-review local-example
```

Frontend lowering resolves fully qualified Interface/input/result selectors with
source spans. Input/result signatures select exposed ValueObjects; their fields
may use the existing bounded value types. Core independently captures originals, checks the kernel and value
relations, and includes its checked projection in the manifest, system graph and
business/system bridge. The generated deterministic `Answer` operation works;
capability descriptors carry formation evidence only. No agent selection, ARE
import, agent resource, listener or provider call is required. Unknown native
calls remain errors. Existing Entry permission and optional-claim admission keep
their original owners.

## Open Questions

C03 owns executable native binding/codecs; M00 owns inference adapters. This
example does not execute a model, document parser or search provider, and does
not qualify an external package/account. See Core `docs/GENERIC-CAPABILITIES.md`
and the reference-application DAG for those separate tasks. Hosting, TDE, EVF
and publication remain deferred.
