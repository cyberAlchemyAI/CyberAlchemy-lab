# Bounded Session-open verification scope

API68’s unchanged inherited timer case still returned `indeterminate` after
83.493 seconds on a 70-second deadline. Its mixed live source/policy/memory
mutation checks passed. A profile of one ordinary Session open is in progress;
no timing fix is qualified from these diagnostics alone.

The next candidate may apply a private per-`Service.call` verification scope
only to the exact selected ReaderChannel/current-legacy `session.open` branch.
It would perform the original complete channel proof before registering any
scope. The already authenticated opaque context, connection and policy SHA
would be retained privately for that call. Each later `channel.guard` would
freshly recheck the sealed captured source basis, every independently pinned
physical family/baseline member, private policy bytes, revocation, period,
principal and actual UTC before returning the same opaque context.

This is separate from the pure eligibility fact-scope registry: dispatch and
journal writes must still occur outside that registry. The verification scope
must be thread-local, non-reentrant and cleared in `finally`; no source result,
permission or clock may survive into the next call. Machine callers and
metadata policy branches keep their original proof paths. Session close keeps
its independent termination path so corrupted Project State cannot prevent
RAM disposal. Actor and caller-context checks remain inside the original
Service logic.

Acceptance requires the unchanged 70-second test, actual physical source and
private policy mutation refusals, captured-memory retarget refusal, opaque
context substitution refusal, distinct concurrent pending plans, and no
cross-call stale proof. A semantic or source-family rebind remains separate
from this performance repair; no full345 qualification is inferred here.
