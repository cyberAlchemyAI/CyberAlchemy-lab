# Application profile generation

`alchlang-generic generate-application` projects an authored business module and
an explicit implementation profile through the existing application library and
Core generator. It creates source artifacts. It does not activate a runtime,
start a listener, contact a provider, obtain credentials or qualify a model.

```sh
alchlang-generic generate-application \
  --project application.project.json \
  --out ./generated-review \
  --accept-local-review local-owner
```

The output directory must be new and its parent must already exist. The owner
argument records an explicit local review and acceptance of the original checked
Core composition. It grants no publication, provider or business effect authority.
The standalone source module also exports `applicationProfileMain(args)` with
the same command and arguments.

## Project contract

The versioned JSON object is closed: unknown fields are errors. All referenced
files belong to the project file's directory or a descendant, use normalized
relative paths, contain strict UTF-8, and are regular nonsymlink files bounded to
1 MiB each. A project may be placed above its business and contract directories.
The compiler captures current bytes and rejects changes during generation.

```json
{
  "schema": "craft.application-generation-project/v1",
  "businessSource": "journey.alch",
  "profile": "contracts/application-intent.json",
  "baseProfile": "contracts/selected-profile.json",
  "native": {
    "package": "@craft/ai-profiles",
    "version": "0.1.0",
    "export": "./application"
  },
  "inference": {
    "kernelTemplate": "contracts/inference-kernel.json",
    "target": {
      "destination": "https://api.openai.com/v1",
      "api": "responses-v1",
      "model_or_harness": "gpt-6-luna",
      "revision": "recorded-fixture-v1",
      "mutability": "immutable"
    },
    "bounds": {
      "max_input_bytes": 65536,
      "max_output_bytes": 16384,
      "max_items": 100,
      "deadline_ms": 300000,
      "max_model_attempts": 1,
      "max_tool_calls": 0
    },
    "mode": "fixture"
  },
  "stageSelections": [
    {
      "kind": "provider",
      "binding": "CrmOperations.HubspotContactSlot",
      "selection": "contracts/contact-effect.json"
    }
  ]
}
```

`profile` contains the existing `craft.ai-application-intent/v1` shape: id,
module, service, scope, operation, types, actual authored `entryAccess`, and
ordered stages. Optional `additionalSources` lists up to eight contained `.alch`
components of the same declared module. The frontend captures their bounded
current bytes; the original library records their authored spans separately
from the technical suffix. Resolved component identities are recomputed and
checked. An optional `sourceSelectionPath` references the current
source-role, projection, policy and target descriptor; this reference receives
the same contained bounded capture and currentness check before the original
library binds `profile.sourceSelection`. The source and Entry remain authored
business inputs. An
existing `craft.ai-application-profile/v1` may also be selected, but each stored
stage digest must match the identity recomputed from the selected owners. Its
authored Entry path may already be absolute when it still belongs to this
physical project directory.
`baseProfile` is an existing transaction/event profile. `inference.kernelTemplate`
is the admitted integration-kernel template consumed by
`createApplicationInferenceSelection`, rather than a second kernel grammar.
The inference object may be omitted when the profile has no model stage.

Install the exact selected `@craft/ai-profiles` package and its matching Core
peer so that public resolution from the project succeeds. The CLI verifies
package name/version, captures the entire physical native package with Core's
public `captureGenericNativeProfileArtifact`, and derives the implementation and
stage digests itself. Project authors do not supply a package hash. Package
exports, imported code and files must still match that capture after projection
and generation. Dependencies remain the separately installed package closure.

The matching Core package is `@domainspec-v2/cli@1.3.0`. Explicit development
selection uses `ALCHLANG_DOMAINSPEC_PACKAGE_ROOT`. The installed public generic
export is preferred even when invoking this frontend's TypeScript source. A
source-checkout fallback uses its public `src/generic/index.ts` only when that
export is absent; compiled installations need no Core source API tree.

## Typed stage selections

A model stage uses the generated binding id returned by the original
`createApplicationInferenceSelection`; its stage kind must be `model`. Its
result remains a proposal subject to the authored Rules and Operations.

A provider selection has exactly `previousOrdinal`, `operation`, `slotId`,
`resourceId`, `action`, `policyId`, `payload`, `receipt`, `provider`, and `account`,
with optional boolean `readCurrent`. A current-read selection is accepted only
when the original connector lists the operation in `identity.readOperations`;
a write cannot be reclassified by a caller flag.
`payload` and `receipt` are the existing declarative field projections. The CLI
checks the selected public connector's original operation list and derives
`applicationProviderSelectionIdentity` over the exact selected package and
selection. It does not instantiate a connector or verify account setup.

Document/index stages use their own implemented contracts:

```json
{
  "kind": "index",
  "binding": "KnowledgeIngestion.PrepareKnowledge",
  "operation": "ingestion.prepare",
  "sourceConfiguration": "contracts/application-sources.json",
  "representation": {
    "model": "text-embedding-3-small",
    "dimensions": 1536,
    "preprocessing": "exact-chunk-utf8-v1",
    "space": "selected-generation-v1"
  }
}
```

The public `knowledgeApplicationStageIdentity` reads the actual business and
source-configuration bytes and combines them with the captured package,
implemented ABI/method, parser/index identities and optional explicit embedding
representation. Supported operations are `ingestion.prepare` and
`ingestion.activate` (`index`), and `rag.decide`, `rag.release`, and `support.review` (`document`).
The helper's actual binding id and kind must match the selected stage. These
roles are separate from inference. Unknown, repeated, unselected or mismatched
bindings fail before artifact creation.

## Generated result and qualification

The new directory contains:

- `source/`: the original business bytes as an unchanged prefix, the library's
  technical mirror, captured authored Entry, bounds, original profiles, native
  selection and Workflow contract.
- `generated/`: the original Core output, including application API, SQLite
  store, Workflow plan and original worker API, graph and source bridge. No second generator or
  business driver is introduced.
- `decision.json`: original local review/acceptance.
- `application-bindings.json` and `origins.json`: supplementary native/Workflow
  joins and source references; original generated graph/bundle bytes are intact.
- `application-system-graph.json` and `application-business-system-bridge.json`:
  supplementary typed model/provider/index/document joins to the original Core
  Workflow, graph and bridge by actual input hashes. Original Core files and
  bundles remain byte-for-byte as generated.
- `application-generation.json`: actual package/input identities, generated
  selection and an explicit `source-generation` qualification. Runtime
  activation, provider setup/wire and real-model quality remain `not-run`.

Validation errors before generation create no output. If original Core
preparation or generation fails after creating the new directory, its partial
artifacts remain available for diagnosis; absence of the final generation
manifest is not a completed generation. Existing directories are never reused
or overwritten.

## Open Questions

Actual runtime setup, Auth grants, provider compatibility, live credentials,
wire behavior and measured model quality belong to the original owners and the
selected integration evidence. The enclosing reference-application objective
owns their consolidated verification; this static command does not complete
those qualifications.
