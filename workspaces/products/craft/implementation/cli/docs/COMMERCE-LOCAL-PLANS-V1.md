# Source-derived local read and effect plans

This candidate internal API preserves original checked commerce source plans as
private handles. It builds on existing Core source reconstruction and semantic
checking. It does not execute a business Operation, apply a State Machine proposal,
open a business database or claim a commit or rollback. Formal claims remain
optional.

`createCommerceLocalPlanOwnerV1` requires the genuine source owner/capture,
semantic owner/capture, source-stage owner/handle and computation-domain
owner/baseline. All must share the exact original captured source. A handle or
manifest reconstructed from JSON cannot supply any parent.

`bindRead(id)` and `bindOperation(id)` derive plans from the original semantic
owner. `checkRead(plan)` and `checkOperation(plan)` accept only exact inert
snapshots of those source plans. They reject dropped fields, changed versions,
changed results and unknown overrides. Inspections expose diagnostic data;
that data cannot restore a plan handle.

Local reads retain their actual predicates, scoped Entity sources, projection
and missing/unavailable actions. Local Operations retain the full ordered tree
of guards, local reads, calls, replay checks, transactions, mutations, events,
results and failure dispositions. `bindTransaction(operation, path)` issues a
private child tied to its original parent. Mutation closures record the actual
record declaration/source/span, complete create/Event fields, update fields,
keys and original-row/expected-version/next-version requirements.

State Machine proposals stay pure. An Operation needs the source transition-tag
guard before reading a proposal state and an explicit transaction before writing
it. The future native store owner must still check the actual original row,
key, expected version and exact single increment before a write. A plan label
cannot provide that evidence.

`bindPureCall(operation, path)` returns the existing genuine source-pure-call
owner and its original binding. Consumers can inspect or compile the pure
component through that owner; it grants no effect or Operation authority.
Disposing the parent Operation also disposes these issued pure-call bindings.
If a source parent has already changed, that original source invalidates the
pure binding; local plan disposal still completes and invalidates its own
handles. This component owns no native resources to drain.
Wrong-owner, cloned, disposed and physically stale parents reject.

Replay conformance and external native-capture protocols cannot be upgraded to
invocable local Operation plans. Native/delegated query producer integration
keeps its original separate task. The existing U0 synchronous pure path is
preserved; eventual effectful invocation requires the separately qualified
asynchronous outcome protocol. Transaction handler execution must use actual
commit/proven-rollback/unknown disposition evidence. Provisional aliases cannot
escape before an original commit.

## Open Questions

The EC15 source plan component is tested. The existing commerce source-stage
route already supplies its checked successor syntax; the old no-effect Alch
application path stays unchanged. Public SDK/native basis integration remains
EC19; local
store execution, remote infrastructure and whole application qualification stay
with their original owners. This internal source API is not yet exported by the
public SDK. Local hosting, TDE, EVF, publication, deployment and live identity,
provider, business database and broker activation remain deferred.
