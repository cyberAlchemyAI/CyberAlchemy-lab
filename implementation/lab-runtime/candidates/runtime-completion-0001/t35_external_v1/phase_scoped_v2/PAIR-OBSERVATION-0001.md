# Phase-scoped pair observation successor, inactive

The reviewed frozen-vector pair produced two Source-child rc 124 timeouts at
the 180-second cap under one 1,703-input selection. Its receipts proved the
same selected application input vector and clean disposable scratch, but did
not record child elapsed time or the package tree at timeout. The earlier
intermittent ContractError remains unexplained. The failed run and all
predecessor source and evidence bytes are retained.

`prefix_pair_observed_0001.py` is a disjoint fixture-only diagnostic. It keeps
the exact 180-second child cap, 128 KiB per output stream cap, two-attempt
limit, 900-second capture/effect watchdog, 60-second episode margin, same
Source→Reader bwrap mount envelope, and immediate O_EXCL attempt receipts.
No historical builder code, marker write, selected input, or protected host
path is changed by this instrumentation.

Each child uses its PID/PGID internally for the reaping and process-group
check. Public receipts retain only `pid_recorded` and `pgid_matches_pid`
booleans, monotonic elapsed milliseconds, whether the direct child was
reaped, and whether that process group was absent at the post-return
observation. The group-absence check waits up to two monotonic seconds after
leader reap to allow namespace teardown, recording the observed wait time.
It refuses if the group remains after that cap. Raw PID/PGID values are never
published. The observation is
bounded: process-group absence at
one instant cannot prove that no other process or transient alias existed.
An unresolved process group refuses package inventory and prevents attempt 2,
even if the scratch directory itself was removed.
The controller records a child-launch attempt before `Popen`; a launch without
a corresponding closed process observation also prevents attempt 2. Ordinary
child exit codes 124 and 125 are nonzero failures; timeout/output-limit codes
require the controller's explicit forced flags.
After the Source child has returned or been killed/reaped, the controller
inventories its owned disposable package tree before cleanup. Public receipts
may name only members of the pinned historical 36-member package plus its
manifest. Unexpected file/directory names are counted, never emitted. A
symlink, hardlink, or other unsafe inventory type yields a closed refusal
flag, never a raw path. Preexisting family leaf hashes are checked unchanged.
Unexpected package leaves or directories, an inventory refusal, or changed
preexisting leaves stop the pair before attempt 2.
The exact disposable scratch path is reported only as a digest with observed
post-context absence. No stdout, stderr, exception text, process argv,
unselected package leaf name, package bytes, or signer content is published.

The outcome remains fixture-only. A timeout is a failure even if package
members appeared; partial output is not Source completion. This probe cannot
measure the builder's internal phases: it records child wall time and the
terminal package tree after child return, not capture/materialization or
per-step builder intervals. A present member may have been written early or
late within the 180-second child cap. This probe cannot
qualify LC-U02-05, protected Source8, actual WSL host deployment, real issuer
authority, Mapper/Context phases, or activation. The previous two-timeout
finding remains open. A distinct exact-hash static review is required before
one new bounded disposable invocation; no timeout increase or blind rerun is
part of this revision.
