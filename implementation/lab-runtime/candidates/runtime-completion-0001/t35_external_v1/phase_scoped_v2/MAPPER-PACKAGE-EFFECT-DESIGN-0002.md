# LC-U02-05 disposable Mapper package effect, design 0002

Status: **inert design / effect HOLD**. This version corrects the 0001
historical-example count. The selected input is
`legacy-session-fixture-mapped-v2-action-0148/build.py` (SHA-256
`dced09f9432318ef286475081ea5f4f7e6fa633c7cefbd9db76c0ec3c47ecbbb`).
It requires **15** current nodes and exactly **10** independently declared
current typed relations. Its request fixes both semantic and governance
cursors at **25**. The selected historical package has 25 semantic and 25
governance leaves plus `request.json`, `native-output.json`, `mapping.json`,
`build-result.json`, and `manifest.json`: **55 files**. A separate diagnostic
instance has 35 events and 75 files; that is a different algorithm/input and
cannot set this selected package's expected closure. The pure 0002 contract
extracts the 15+10 predicates and both cursors from the pinned builder, and
rejects any proposed event count other than 25. A later effect must verify
the fresh signed cut yields those selected counts; it must not invent rows.

The selected builder's intended sequence is guard, package creation, two
native `seal-fixture <input>` calls, numbered semantic/governance emission,
request emission, two identical cold native reads with arguments
`<semantic-dir> <governance-dir> <request.json>`, then native output, mapping,
result, and manifest emission. `mapper_package_plan_0002.py` renders full
candidate read-only Bubblewrap/loader argv for all four calls and rejects any
additional mount or argument. It does not launch a process or validate
nonempty native output. The native CLI source has exactly those two forms;
the first seals in-memory events, and the second reads a native cut without
writing a store. A future effect must enforce bounded output, exact event
digests/cursors/joins and byte equality of the two cold reads. The selected
historical package's bytes are evidence of its own past run, not a substitute
for fresh Source→Reader→Mapper computation.
The governance input is not independent: the historical builder constructs
all 25 governance `semantic_ref` joins from the **first sealed semantic**
event digests and cursors, then seals governance. The mediator must enforce
that staged dependency and reject precomputed or reordered seal inputs. A
read-only replay of the checked-in historical 25-event package could diagnose
native compatibility, but cannot qualify a fresh disposable package.

The current generated builder still has five effect refusals: one package
`mkdir`, two `emit` sites, and two `seal` sites. Its `call()` routes to
`runtime_bridge.run_native`, which refuses. The original builder also
requires `mapped/packages/0001` to be absent and then creates it. An exact
read-write mount of only `0001` requires that directory to be precreated.
That conflict needs a versioned exact-preimage builder adapter that checks
the precreated directory is empty and held; replacing the refusal with
general filesystem or subprocess access is not a valid repair.

The effect design retains the fresh v5 Source→Reader→Mapper predecessor and
held byte checks. After those complete, a separate Mapper package child sees
the snapshot, family and generated roles **read-only**. It receives no
read-write bind of the package or any other host path. A narrow inherited
IPC descriptor carries exact write and native-call requests to an external
mediator; the descriptor transfer, peer identity, message framing, budgets,
and closure still need an effect design and adversarial tests. Only the
mediator owns a held writable `mapped/packages/0001` dirfd. It accepts only
exact numbered event leaves and the five fixed leaves, creates them
no-replace, fsyncs, reads back, and verifies the closed 55-file inventory.
The two seal inputs pass to the mediator as bounded bytes in the required
semantic-then-governance order and are materialized in private scratch outside
the family. Each native child
receives copied selected ELF/ABI leaves read-only, one read-only seal input or
read-only package mount, no protected roots, and no writable mount. The
Bubblewrap nested-mount behavior and nonempty native outputs remain to be
tested before an effect candidate is reviewable.

The controller must gather poststate through held nofollow directory and
file descriptors. A name-set comparison alone is insufficient: the only
directories may be package root, `semantic/`, and `governance/`; all 55 leaves
must be regular single-link files, with expected owner/group and effective
0600 mode, no symlink or hardlink, and no extra directory. The manifest's
`files` must bind exactly the 54 non-manifest leaves and their observed
hashes. The pure inventory model rejects bad metadata and hash sets, but
does not itself inspect live filesystem custody. The controller must retain
its evidence-root lock, no-replace attempt and
result publication, child deadlines, held original process-group identities,
and scratch on UNKNOWN. After the package child, it verifies fresh
predecessor bytes, the 55 leaf names and hashes, manifest/source/Reader/Mapper
bindings, native replay parity and no-authority fields, and the absence of
Context and activation artifacts. The historical Context path separately
pins the Mapper manifest and replays the cut; it is outside this slice.
Original-group closure cannot exclude escaped-session descendants; protected
host qualification still requires the LC-U03-02 cgroup oracle. No protected
Source8 authority, Context effect, activation, or LC-U02-05 acceptance follows
from this design or its synthetic tests.
