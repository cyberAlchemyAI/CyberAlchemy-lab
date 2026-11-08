# Explicit owned workflow currentness

This workspace implementation resolves output originals through a selected private
journal's committed HEAD, original transaction digest, coordinating Actor, Work, Run,
scope, Source cut and producer receipts. Producer receipt paths are selected
independently by the host, with an exact closed set and fresh private original
byte checks at entry and exit. It rechecks the host guard and original
bytes before returning a fact. Orphan blobs, unheaded transactions, altered bytes,
foreign selections, changed HEAD and later committed revisions are not current.
Revision retirement is scoped to the same identity and carrier. A future
cross-carrier identity migration needs a separate retirement contract and test.
The returned posture is `owned-produced-current`; retained Session evidence does
not reactivate a Session or confer permission.

`owned_kernel.py` is a disjoint private coordination profile. Every original plan
predicate is retained except the explicit typed currentness provider. Entry and
exit invoke the live guard. The original strict kernel, states, transitions,
required carriers, obligations, actual grant period and no-admission flags remain
unchanged. A dictionary in a wire request cannot select this private profile.
`HostHeaders` delegates source/coordination validation to trusted host adapters;
it does not itself verify their record bytes, schemas or semantic relations.
Those adapters and native first-emitter integration remain necessary before this
component can prove a completed native WorkflowRun.

The host selects `Selection`, provider callables and transaction digests outside
the request. `host_guard` must independently verify current Source, exact Actor,
private grant, revocation, scope and actual UTC on every call. It must also verify
the selected producer receipts' actual method, request,
reply and source lineage; matching receipt hashes alone cannot establish that.
The actual producer Actor may differ from the coordinating Run Actor and must
be verified separately through those originals.
Component tests use explicitly synthetic host proofs. They establish no current
Source or grant.
Same-UID arbitrary code/memory replacement and concurrent hostile filesystem
writers are outside this managed exclusive-writer component's guarantees.

Run both modes without creating bytecode in any selected source tree:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover \
  -s implementation/lab-runtime/local-host/t31-owned-produced-0001 -p 'test_*.py' -q
PYTHONDONTWRITEBYTECODE=1 python3 -B -O -m unittest discover \
  -s implementation/lab-runtime/local-host/t31-owned-produced-0001 -p 'test_*.py' -q
```

This depends on the pinned workspace output-store adapter, API30 journal/kernel,
original schemas and carrier catalog. It is not a standalone runtime package.
T31 remains open until actual producer outputs, complete selected host adapters
and later consumers run together, with per-template dispositions.
