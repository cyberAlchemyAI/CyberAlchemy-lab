# Historical Mapper replay: bounded-launch feasibility

Status: **inert assessment; effect HOLD**. This note responds to the independent
v3 primary review (`independent-historical-mapper-replay-effect-static-review-0003-primary.md`,
SHA-256 `5fa5be66453d31b37d9b1ee8152ed9b9d4113e72445cdf4d247d76ae7c1cfeec`).
V1–v3 remain frozen and none is authorized for preflight or effect. No
Bubblewrap/native child or launch prototype was run for this assessment.

The selected diagnostic is noncritical: it would only reread the checked-in
historical 25-event Mapper package and compare two native outputs to a past
file. It cannot construct a fresh same-scratch Mapper package, prove protected
Source8 authority, qualify the host, or accept LC-U02-05. The v3 launch gap
therefore does not justify adding a new trusted process launcher now.

`Popen` and `os.posix_spawn` preserve convenient exact argv/environment/pipe
setup but do not give this controller a child identity while launch is stuck.
On current glibc, `posix_spawn` starts with `CLONE_VM|CLONE_VFORK`; the parent
may remain suspended until child setup/exec completes, so replacing `Popen`
with `posix_spawn` alone does not repair the pre-return watchdog gap. Python
does expose `setsid`, file actions and signal-mask controls for `posix_spawn`,
but those configure the child, not an independently enforceable bound around
the call. See the [Linux posix_spawn manual](https://man7.org/linux/man-pages/man3/posix_spawn.3.html)
and [Python `os.posix_spawn` documentation](https://docs.python.org/3.14/library/os.html#os.posix_spawn).

An explicit fork/exec path can return a PID to the parent before the child
execs, with precreated `O_CLOEXEC` pipes and child-side `setsid`, `dup2`, FD
closure, fixed environment and exact `execve`. That is a possible research
direction, not a reviewed replacement. A Python post-fork child must avoid
unsafe runtime work in a multithreaded process; Python warns about this use
of `fork`. The watchdog/child-identity handoff around a stalled or interrupted
`fork` still needs proof, as does custody when child setup fails before
`setsid`. A subsequent `pidfd_open(pid)` can bind an unreaped child, but does
not close the interval before the PID is returned and does not contain
descendants that leave its process group. See [Python `os.fork`](https://docs.python.org/3.14/library/os.html#os.fork)
and [Linux pidfd_open](https://man7.org/linux/man-pages/man2/pidfd_open.2.html).

A small native broker using `clone3(CLONE_PIDFD)` could obtain PID and pidfd
from one creation syscall and perform only fixed child setup before exec.
It would add a trusted binary, ABI/syscall availability checks on this WSL
kernel, an exact error channel, FD-inheritance review, signal-mask and session
review, and an independent watchdog that remains active if the broker itself
hangs. A pidfd identifies a leader; it does not by itself prove original-group
or escaped-session absence. An exclusive cgroup with externally observed
kill/empty semantics could address unknown descendants, but that is the
unaccepted LC-U03-02 host qualification, not a property of this disposable
historical replay. See [Linux clone3](https://man7.org/linux/man-pages/man2/clone.2.html).

If this diagnostic is revived, first build and independently review a bounded
spawn/containment primitive as its own unit. It must prove a pre-effect durable
attempt marker; exact 37-token argv and `LC_ALL=C` with only intended pipe FDs;
fresh session/group identity; immediate parent custody of every launched
child; a watchdog that can terminate a stalled launch without depending on
the blocked launcher; bounded wait/reap and no-replace sanitized FAIL on
unknown closure. Fault tests must stall before PID handoff, during child setup,
at exec failure, and across watchdog delivery, then check no unowned child or
open sensitive FD remains. On the current evidence there is no such proof.

Decision: **leave the historical read-only replay effect HOLD**. Preserve its
pure selection and v1–v3 review history. Continue the original execution plan
on work that does not depend on this optional historical diagnostic; do not
weaken the 5/30/90-second contract or claim that an unbounded launch is safe.
