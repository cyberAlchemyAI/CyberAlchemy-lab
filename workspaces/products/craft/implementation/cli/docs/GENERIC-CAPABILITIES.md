# Generic capability contracts

P01 extends canonical contract data; C01 carries selections through Alch and C02
checks original source/authority ownership. C03 now emits executable fixture resource wiring and business-type codecs.
Real provider/harness adapters remain separate M00/G01 tasks. A descriptor or
fixture result is not a working qualified provider.

Business authors keep the existing thirteen meta-types. An existing Interface
can expose the business input/result values without embedding a vendor:

```alch
interface Model:
  kind bounded-schema
  exposes Request, Reply
```

The selected application profile is unchanged. A separate
`craft.generic-capability-selection/v1` record maps the fully qualified Interface
to an explicit `inference/v1`, optional `agent-run/v1`, `document/v1` or `search/v1`
contract. All fields are closed and bounded in
`contracts/generic-capability-v1.schema.json`. Canonical generation owns both Core
and Alch data types; there is no second handwritten schema.

`validateGenericCapabilitySelection(selection, kernel)` reuses the existing
integration kernel validator for provider profiles, resources, failure mappings
and completion evidence. `kernel.sha256` is the canonical JSON digest produced
by `dataDigest(kernel)`; source/profile digests bind the exact authored file bytes.
The physical owner separately captures selection/kernel paths and currentness.
Required operations/capabilities must exist on the exact selected realization
and provider profile. Bounds cannot exceed the selected implementation. Missing,
duplicate, unused or mismatched bindings reject before generation output.

Inference admits text, checked structured text and dimensioned embeddings as
different operations. It has one logical model attempt and no tool execution.
Agent runs have exactly one selected harness and optionally typed read-only Query
tools. Ordinary external business APIs retain their existing contracts. No new
provider keywords or universal executable adapter hooks are introduced.

Descriptors bind exact package version/digest/export, destination/API/model or
harness revision, fixture/provider mode, schema subset, bounds and lifecycle
references. Existing kernel secret slots/resource bindings retain credential
ownership. No automatic fallback is allowed; unknown effects require
reconciliation. Streaming, effectful tools, arbitrary SQL/filter scripts and
implicit provider routing are unsupported in these contracts.

The schema also defines complete source-context dependencies, single-use release
ticket **data**, trusted search context **data** and closed continuation decisions.
Validating these records grants no authority. C02 must require original owners;
caller/model-provided tenant, grants, source access or release-ticket JSON cannot
become an executable authorization. Retries require proven-not-dispatched
evidence and finite attempts. Context dependencies retain ACL and policy revisions,
including non-cited inputs and tool results.

The existing composition SDK accepts optional `capabilitySelectionPath` alongside
`sourcePath` and `profilePath`. `inspectCapabilities(handle)` returns the checked
formation projection. Generation includes `capability-bindings.json` and exact
source/profile/kernel/provider/resource/adapter links in its manifest, system graph
and business-system bridge. Native calls require the generated dispatcher and its original composition owner.

`createGenericCapabilityContextOwner(composition, handle, runtime)` requires the
actual same-application SDK/runtime registry join. Its bounded single-scope tenant
is the checked Entry's `access.scope`; actor and grant revisions come from current
native Auth READY frames. It does not accept a caller's tenant/grant JSON or
implement general multi-tenant/source-ACL mapping.

Optional tools have one exact Entry parameter `ValueType` codec and the exact
result codec, including UInt64 inputs and optional Query records. Execution uses
the original protected Query path and rechecks root/tool grants, cancellation,
deadline, fence and source snapshots after awaits. The original SQLite owner
captures opaque Query snapshots; any own or external store mutation invalidates
them conservatively. These snapshots are local Query disclosure custody, not
external-source revisions or durable egress release tickets. Only declared Query
Entity scope is supported. A new context supersedes the previous context in the
same context owner; parallel durable agent-run custody belongs to the later harness
work.

Search handles admit bounded requests against a checked Entity/Query scope, finite
`eq`/`in` filters and declared Bool/UInt64/string/literal codecs. They do not execute
ranking or an index. Record/refinement/filter scripts, raw SQL, user-issued
credentials and arbitrary collection access reject.

## Generated executable bindings

Generate through the existing accepted composition handle. Its manifest now has
`capability_wiring`; the same output directory contains `capabilities.mjs`,
`capability-wiring.json`, `capability-coverage.json`, and each binding's input/result
JSON schema and standalone decoder. The system graph and business-system bridge
link the exact business selector, source/profile/kernel hashes, native resource,
contract, realization, schema and decoder. Agent tool links also name the original
Entry parameter and its argument/result codecs. Coverage counts selected bindings
and tools, with generated/linked evidence; it does not claim provider execution.

```javascript
const api = await import(generatedCapabilitiesFileUrl);
const dispatch = api.createGeneratedCapabilityOwner(composition, handle, {
  consumerRoot: absoluteConsumerDirectory,
  // runtime: original same-application runtime, required for protected Query tools
});
try {
  const result = await dispatch.invoke(bindingId, utf8JsonBytes, {
    deadline_ms: Date.now() + 1000,
  });
  // result.value is checked; result.wire retains canonical UInt64 decimal strings.
} finally {
  await dispatch.close();
}
```

Agent callers first use `dispatch.openContext(actor, rootEntry, bindingId, settings)`
and pass that opaque context to `invoke`. Tools run through the original protected
Query owner. Root permission and every used tool permission are checked again at
the final disclosure after native work. Caller JSON cannot substitute this context.
The existing HTTP/keyed bundle writers preserve the capability selection, kernel,
generated files and hashes; bundle readers reconstruct the same original owner.
No provider starts on import and there is one application runtime.

The first native ABI is `craft.native-capability-resource/v1`. A selected installed
package exports `createCapabilityResource(selection)` and returns an exact frozen
resource with declared operations/capabilities, an `invoke(request)` byte interface,
and exactly the selected harness owner for `agent.run`. The package must be found
under the explicit consumer's `node_modules`, with exact name/version/export and
whole-package digest: `dataDigest({schema_version:
'craft.native-capability-package-bytes/v1', files})`, where `files` is the sorted
portable inventory of every regular file's relative path, SHA256 and byte count.
There are no ignored files. This initial profile admits at most256 files/16MiB of
self-contained static UTF8 ESM and a small declared builtin set; nested dependencies,
symlinks, private/bare imports and dynamic loaders reject. It runs trusted native
code, not a sandbox. Async load/invoke/tool waits have deadlines and cancellation;
abandoned invocations cannot dispatch again or revive tool access. Synchronous
trusted code cannot be preempted. **Only fixture mode executes** here; provider mode
rejects before module loading until M00/G01 supply the real adapter boundary.

## Installed native profiles and durable stages

The application-profile path uses `captureGenericNativeProfileArtifact` and
`createGenericNativeCapabilityHost` for explicitly selected installed native
packages. It extends the earlier self-contained fixture dispatcher above. The
operator selects an exact package/version/export and the computed whole-package
identity; missing or modified bytes reject. The package inventory is bounded to
1024 regular files and 64 MiB, excludes nested dependencies, and rejects links.
Declared external dependencies retain their own exact install closure and locks.
This is trusted native code, not an isolation sandbox.

The host requires the original accepted composition, its generated codecs, its
same-application runtime and original Entry actor. An invocation authorizes through
native Auth before loading/calling the selected module and again after awaits.
The authorized input digest is the canonical generated business wire, preserving
UInt64 decimal strings. A host-only invocation view retains the original actor;
it is never serialised to a model or accepted as caller JSON. Source disclosure
is checked by the configured original owner before the result is returned.

`registerGenericWorkflowStagePort` connects this boundary to the existing durable
workflow driver and SQLite journal. Each non-local stage binds the actual native
capability digest into the workflow contract. Inspection precedes execution;
unknown outcomes remain unknown, and only a proven not-dispatched observation
allows a new attempt within authored bounds. Resource currentness and the active
workflow claim are distinct checks so a child registration cannot recursively
re-enter its parent claim check. No provider call occurs merely by importing or
generating a profile.

The shared application-profile package supplies the M00 inference and optional
G01 agent adapters. Local recorded transport execution exercises the actual
SDK/codec/continuation path. Credentialed provider qualification, real model
quality and deployment remain separate, unrun scopes. Direct applications require
the model transport package, not the optional agent harness.

## Strict result types

Schemas and decoders derive from the same checked business type. Exact UInt64 uses
canonical decimal strings up to18446744073709551615. Field renames change both
artifacts. Finite bool/UInt64/string/ASCII-refined values, simple enums, records,
lists and optional values are supported where the strict schema exactly expresses
the checked type. Reached record invariants/collection predicates, cycles, tagged
outcomes/enums, nested optional values and Unicode byte restrictions not exactly
representable by JSON Schema reject before output. They are not silently omitted.

Embedding results have the explicit technical selector `Craft.Native.FiniteVector`,
required only by `vector.embed`; no fake business record or new business numeric
type is needed. Its dimension comes from the selected embedding contract. The
schema and decoder require exactly that many finite IEEE754 binary64 numbers,
reject wrong dimensions/nonfinite values, and normalize negative zero. This does
not introduce approximate numbers into business UInt64 calculations.

## Open Questions

C03 implements the finite generated bindings described above.
R02/R04/R05 own durable source release, accounting and continuation execution;
M00/G01 own inference/harness adapters. Package/account/model qualification remains
unrun until those selected implementations execute. See the reference-application
design and DAG under `goals/plans/craft-ai-reference-applications-2026-10-30/`.
Local hosting, TDE, EVF and publication remain deferred.
