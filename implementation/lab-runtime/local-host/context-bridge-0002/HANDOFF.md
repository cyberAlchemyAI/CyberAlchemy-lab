# Context bridge/writer prototype 0002

Effect-disabled disjoint correction. No original Context, private archive, key,
policy, Docker or native effect is enabled or run. Only owned disposable files
and same-process AF_UNIX socketpair fixtures are exercised. Construction/closure
lanes and every bridge0001 byte remain unchanged.

Selected predecessor: `context-bridge-0001/freeze.json`
`5d7ddf184ade751d4b37101a72c7e3555daa5c8659e759a5b7d827a48cf33e3a`.
Independent HOLD:
`CONTEXT-BRIDGE-INDEPENDENT-STATIC-REVIEW-0001.md`
`5f3f8073d7924ba2e52856f74484049ea52a5817c5cac66c1f466b4c9f815a83`.

## R01: parent close completion precedes final verdict

`Mediator.run()` now sets `socket_closed=True` only in the successful return
branch of `sock.close()`. An exception leaves the flag false and state UNKNOWN.
`run_completed` is set after that close outcome is recorded.

The mediator owns its serving thread through `start()`. `join(timeout)` performs
the actual join and records completion only when that thread is no longer alive
and `run_completed` is true. `final_verdict()` checks this managed join,
non-running thread, completed run, successful parent socket close, peer EOF,
writer close and client completion. A caller flag or assumption that `run()`
probably returned cannot satisfy it. A failed close is attempted once and never
retried. Thread/boolean objects are a trusted local implementation boundary,
not isolation from arbitrary Python mutation.

The new causal tests hold parent close behind an event after client completion.
During the block, client state is SUMMARY_PERMITTED and mediator state PEER_EOF,
but socket_closed and run_completed are false, a bounded join reports incomplete,
and final_verdict refuses. Releasing the event into an OSError still refuses.
A separate successful-close control permits finality only after the managed
join. Directly joining the thread without the selected mediator completion API
does not publish a final verdict.

## R02: original child output is private until aggregate completion

`ProvisionalOutput` is a fixed parent-owned bounded capture sink. The selected
original build-tail print calls `capture`, not external stdout. Capture retains
one exact UTF-8 line, at most 8192 bytes; extra calls or invalid input poison the
buffer. It never emits or returns the provisional line.

After managed mediator join and aggregate success, `release(client, mediator)`
checks the exact original summary shape, result, current selected manifest
path/digest, carrier count, posture and zero added public operations. It compares
canonical encodings to avoid bool/int equality aliases. Only then can it return
the unchanged original line once. A failed or premature release becomes sticky
UNKNOWN. The selected fixture/controller exposes that returned line only after
this method succeeds; the internal transport verdict alone is not a publication
operation.

A parent close failure after the original print now leaves **zero exposed
child lines**; the line stays private in the buffer and release refuses. Tests
cover blocking/failing parent close, successful delayed release, missing managed
join, invalid/oversized/repeated capture, wrong manifest-summary fields and
repeated publication. The byte sink implements the same-process AST fixture
seam only. Bounded OS child stdout/stderr pipes and child exit/provenance remain
future controller work; this candidate does not pretend they exist.

## Unchanged protocol and claim ceiling

The writer, original payload encoding, original eight-field manifest, exact
40 leaves and 39 manifest bindings remain unchanged. There are 38 leaf EMITs,
then separate RELEASE_PRIVATE, result leaf39, manifest leaf40, sole FINISH
action41: 42 requests in total. Per-leaf file/name fsync and exact readback
precede ACK. Writer close and postclose readback precede FINISH ACK; checked
client close precedes the original print into the private sink. Failure poisons
the attempt without reset/retry or deleting retained originals.

The tests still extract only the selected original emit function, final five
build statements and Source encoded() function. They do not import or execute
a complete original role or access original private data. Every test checks
owned FD and thread counts after fixture cleanup. Normal and optimized selected
runs and their actual OS exits are retained in report.json.

All predecessor limits remain: mode0444/0500 and no client write API are not
OS confinement against the same UID; credentials prove only a checked local
tuple; the private directory is empty and synthetic, not a real policy/key
lifecycle; successful fsync is not a power-loss proof; the 30-second deadline
does not bound an uninterruptible kernel call or parent death; no restart
adoption, durable distributed final receipt, Docker fd3 route or actual Context
source/runtime/schema closure is supplied. The 64-KiB leaf, 100000-byte frame
and 2-MiB total ceilings are still unproven for a real Context package.

Independent exact-byte review is required. No original-task acceptance,
protected Source8 authority or real local Context readiness is claimed.
