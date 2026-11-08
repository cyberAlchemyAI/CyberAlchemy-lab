# Historical Mapper package cold-replay diagnostic 0001

Status: **inert candidate; no effect or preflight published**. The pure module
`historical_mapper_replay_0001.py` has no launcher or writer. It selects the
checked-in historical `legacy-session-fixture-mapped-v2-action-0148/packages/0001`
only. That package is 55 mode-0600 regular single-link files (25 semantic, 25
governance, five fixed leaves), 781,575 bytes, with inventory SHA-256
`e38101f67689dc56ba23815a6d6017125bbb391e64757dff643c52876095b4d6`.
Its request pins semantic and governance cursors at 25. The expected historical
native output is 221,942 bytes at SHA-256
`669b5eced4988dbe4fdf562ab82ad605ce671cd37490ec75251e94f06c680177`.
The module independently pins the exact Bubblewrap, ELF, loader, libc, and
libgcc bytes and modes from the selected 0004 runtime installation. Its
`static_preflight()` reads only selected bytes and refuses drift, aliases,
extra leaves, missing leaves, or cut mismatch. It does not prove future mount
identity or execute a process.

The next separately reviewed effect controller should use the v5 native-seal
smoke's held nofollow capture, selected-copy verification, process-group
observation, watchdog, and no-replace publication patterns, adapted for the
55-file package and two native reads. It must copy the exact package bytes into
one fresh private `/tmp/lc-u02-05-historical-mapper-replay-*` scratch tree,
recheck source and copied package identities/hashes immediately before and
after each launch, and retain held directory and leaf descriptors across
both. Runtime copies should be executable only where required (Bubblewrap,
ELF, loader: 0500; libc and libgcc: 0400). Package copies should be 0400 with
0500 directories inside owner-only scratch. Refuse any unexpected file,
symlink, hardlink, replacement, mode, owner, size, or hash. No historical
package byte may be written and no checkout, Source8 material, protected
root, network, device, `/proc`, or writable mount may enter the namespace.

For each of **two fresh native child processes**, pass the same exact
`replay_argv(scratch)` through a newly launched selected Bubblewrap binary.
The five read-only mounts are the selected native ELF, three selected ABI
leaves, and copied package directory. The loader receives
`--inhibit-cache --library-path /work/abi /work/native` followed by exactly
`/work/package/semantic /work/package/governance /work/package/request.json`.
The controller must verify selected Bubblewrap version `0.11.1` first, with
its own bounded version child. The native children get a 30-second monotonic
deadline each, independent 262,144-byte stdout and 256-byte stderr ceilings,
and a 90-second aggregate watchdog. Drain both pipes while monitoring the
leader; EOF is not process exit. Hold the original group leader unreaped with
`waitid(WEXITED|WNOWAIT)` while observing the original group. Forced cleanup,
unknown group membership, signal failure, uncertain child launch, or an
unclosed descendant forbids PASS and retains the owned scratch. Never signal
a numeric PGID after its leader is reaped. The selected historical stdout
bytes must equal both replay outputs byte-for-byte; both stderr streams must
be empty, return codes zero, and closures independently observed. Raw output
stays in scratch/memory and is never put in the public receipt.

Use new no-replace names `historical-mapper-replay-attempt-0001.json` and
`historical-mapper-replay-result-0001.json` under the LC-U02-05 evidence
directory. Under a held, exclusively locked evidence-root dirfd, refuse an
existing attempt, result, or retained result temp. Before the first child,
write/fsync/read back a mode-0600 `O_EXCL|O_NOFOLLOW` attempt marker binding
controller, pure plan, tests, package inventory, runtime leaves, full argv
digest, limits, and result name; retain it on every outcome so a crash or
failed publication cannot authorize another run. Publish one sanitized result
through an exclusive temp plus no-replace hard link, fsync and read back;
never replace the final leaf or remove the attempt marker. Receipt fields
must include each child's launch/exit/closure/forced-cleanup observations,
actual argv digest, output lengths and SHA-256, copied package/runtime hashes,
marker binding, scratch cleanup or UNKNOWN retention, and explicit no-authority
fields. A failure of result publication remains an uncertain attempted
effect, never an invitation to replay under these names.

Even a future two-replay PASS would prove only that this **historical checked-in
25-event package** can be read twice by the selected native binary in a
disposable Bubblewrap namespace. It would not construct or qualify a fresh
same-scratch Source→Reader→Mapper package, resolve the original protected
Source8 authority/host gate, prove absence of escaped-session descendants,
produce Context, accept LC-U02-05, or authorize activation. Actual host
containment still needs the LC-U03-02 cgroup oracle.
