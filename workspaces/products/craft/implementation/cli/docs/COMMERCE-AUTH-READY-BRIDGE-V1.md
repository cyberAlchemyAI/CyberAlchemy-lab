# Commerce native authorization and entry context v1

This candidate component connects checked `.alch` entry-point permissions to the
existing Auth Foundation Rust admission and decision implementation. It issues
private, single-use authorization handles for one logical entry and one decoded
input. Formal claims are optional; none are required by this component.

This is an internal source API. The public package exports and installed SDK
have not been extended here. The public application basis and protected runtime
joins retain their existing EC19 and EC21/EC28 tasks.

## Source and execution

The implementations are
[`commerce-auth-ready-bridge-v1.ts`](../src/commerce/commerce-auth-ready-bridge-v1.ts),
[`commerce-entry-context-v1.ts`](../src/commerce/commerce-entry-context-v1.ts),
and the new Rust crate
[`commerce-auth-ready-bridge-v1`](/home/vlad_/projects/cyberAlchemy-v2/auth-foundation/implementation/commerce-auth-ready-bridge-v1/README.md).
The controlling source profile is
[`auth-bridge.json`](/home/vlad_/projects/cyberAlchemy-v2/examples/ecommerce-target-candidate/profiles/auth-bridge.json).

The entry owner requires original Core source, stage and computation-domain
handles and an actual native producer. It reconstructs entry permissions,
principal-context field types and argument schemas from captured source. It uses
the existing generated value codecs to validate and canonicalize input bytes.
Customer context never comes from request JSON.

The native producer is an explicit developer build step. It runs fixed
`tools/toolchain/run cargo metadata/build --offline --locked` commands against
the new crate, records actual resolved package sources and tool files, and
copies the produced executable into a fresh private directory. It pins the
original executable, captured source/tools and observed shared libraries.
It does not substitute a compiler when an execution artifact is missing.
These observations are a native component identity; they are not a hermetic
compiler/sysroot attestation or the complete application basis.

The fixed executable accepts one bounded owned stdin frame, calls the original
read-only Auth admission transaction, copies READY metadata while READY is
borrowed, and consumes READY through the existing fixed decision implementation.
An allow response is sent only after the transaction finishes successfully.
Request IDs, logical entry, operation, input/source/profile/native identities,
actor identity, target service and declared parent scope are echoed and checked.
Resolved policy content is hashed, not inferred from a revision label alone.
UInt64 revision, time and epoch fields use exact decimal strings.

## Internal API sequence

1. `produceCommerceAuthNativeOwnerV1(freshAbsoluteDirectory)` creates the actual
   registered native owner. Neither a manifest nor a JSON clone can replace it.
2. `createCommerceEntryContextOwnerV1(sources, capture, stage, source, domain,
   baseline, native, freshAbsoluteDirectory)` captures the source-derived codecs
   and retains the original parents.
3. `bindEntry("Orders.PlaceOrderEntry")` selects a declared logical entry and
   its inline permission. `prepareInput(entry, bytes)` returns an input handle
   with copied, validated canonical bytes. Unknown and private-context fields
   in the wire object reject.
4. The **test-only fixture provider** creates a fresh private Auth SQLite
   namespace and seeds the actual existing Auth schema. The internal
   `registerCommerceEntryFixtureActorV1` accepts only that native owner's private
   database handle and a validated fixture assignment. It is absent from public
   package exports. This is a declared test trust boundary; a production token
   provider is not implemented here.
5. `authorizeCommerceEntry(actor, entry, input)` performs the actual native
   decision and returns either a private authorization handle or a 401/403
   result. A customer subject, service caller and tenant must match the actual
   READY decision and source entry. Calling service and target service stay
   distinct.
6. `consumeCommerceEntryContext(context, entry, input)` atomically claims the
   handle before awaiting anything, repeats the native decision, and compares
   subject/session/permission/evidence/revisions/full policy snapshot. It returns
   a private invocation authorization only if all parents remain current. A new
   native request ID, time and evaluation epoch are expected on the repeated
   decision; the original immutable invocation binding stays the same.
7. `principalScope`, `resourceScope`, `inspectScope` and `inspectInvocation`
   expose the corresponding authorization facets and diagnostic views. Views
   cannot reconstruct any private handle. Disposing the entry, input, actor,
   authorization or owner invalidates the dependent facet.

Two handles containing identical canonical bytes are still distinct original
inputs. An authorization for one cannot be consumed for the other. A different
logical entry cannot consume it, even if it invokes the same Operation. A second
or simultaneous consumer is rejected. Failure during consumption retires the
handle.

## Resource and effect boundary

The resource facet describes the actual Auth permission's resource, action,
scope and subject. It does **not** establish ownership of an order row, quote,
worker lease, event delivery, journal record or command receipt. Inspection
preserves the source's business-resource bindings and resource condition and
explicitly sets `actual_business_resource_owners_qualified: false`.

The customer facet's invocation/command identifier names this authorization
invocation; it is not an idempotency or business command receipt. The service
facet records the authenticated calling service and target; it does not create a
parent-customer delegation, worker claim or event owner. This component uses a
null causal-owner identity until a later genuine resource owner supplies that
join. It never invokes a business Operation or applies an effect.

Permission fields are observations of the successfully consumed decision.
Business execution must still use the later runtime owner and its transaction
and resource checks. The facets are not durable grants or proof that subsequent
independent execution remains authorized.

## Process limits and settlement

| Bound | Exact value |
|---|---|
| Requests per child | 1 |
| Input bytes | 4096 |
| Output bytes | 8192 |
| Active children | 4 |
| Queued requests | 64 |
| Startup and evaluation deadline | 2000 ms from accepted submission |
| Cancellation escalation | SIGTERM, then SIGKILL after 200 ms if still pending |

The parent uses a monotonic absolute deadline, including queue time. Event-loop
delay cannot turn a late response into success. Only a valid single response,
zero exit, no signal, no stderr, current database identity and current native
component can mint a completion. Extra/duplicate/trailing/malformed output,
wrong request/binding/permission and invalid exact numeric fields reject.
There are no caller-supplied child command, environment or policy callback
arguments.

Timeout, abort and disposal reject the result but retain the active slot and
pipes until actual child close. Native `dispose()` returns only after actual
owned children settle; repeated callers await the same settlement. Context
owner disposal invalidates its own handles synchronously. It does not dispose a
shared native owner or claim that its children have settled; the application
owner must also await native disposal.

Fixture database contents can change for genuine revocation/snapshot tests.
Their original file and directory identities and private modes cannot be
replaced. Identity is rechecked on submission, before queued work starts and
before accepting a child response. This is an isolated local fixture boundary,
not protection against an adversarial operating-system administrator.

## Validation

From the repository root, run the source tests without rebuilding the public
SDK:

```sh
cd craft/projects/domainspec-v2/impl/cli
node --import tsx --test --test-concurrency=1 test/commerce-auth-ready-bridge-v1.test.ts test/commerce-entry-context-v1.test.ts
node node_modules/typescript/bin/tsc --noEmit --incremental false
```

The tests build the actual fixed Rust program, create private scratch Auth
fixtures, exercise the original checked ecommerce sources and generated codecs,
and leave task-local receipts/artifacts under the EC11 evidence directory.
Only fresh private fixture copies are changed by replacement/currentness tests;
canonical sources, earlier SDKs and previous task evidence stay unchanged.

## Open Questions

The original plan owns follow-on application/native basis integration (EC19),
actual protected entry and Auth join (EC21), and worker/journal/call custody
(EC28). Production authentication-provider registration, real business resource
ownership and effect execution remain with those owners. This component alone
does not qualify installed protected application generation. Local hosting,
TDE, EVF, publication, deployment and live provider/database/broker activation
remain deferred.
