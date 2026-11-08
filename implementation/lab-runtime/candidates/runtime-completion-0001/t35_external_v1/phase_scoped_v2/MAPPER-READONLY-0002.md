# LC-U02-05 delayed Mapper native selection, version 0002

The first reviewed Source→Reader→Mapper read-only attempt is a sealed **FAIL**:
`phase-mapper-readonly-result-0001.json` reports `CONTRACT_REFUSAL` at
`mapper_materialize`, with both children reaped and scratch removed. A
read-only check found that the authentic 1,703-row Source selection excludes
the native executable, while the first Mapper projector assumed it was in
both Source and Reader selections. The receipt does not identify the exact
predicate, so this is a grounded correction hypothesis, not a retrospective
claim that a later Mapper import ran.

Version 0002 keeps the Source and Reader input vector and their manifests
unchanged. After a fresh Reader success in the same owned scratch, the
controller holds and checks the exact repository native leaf at the fixed
`runtime-dependencies-v2-completion-0001/installations/0004/bin` path:
SHA-256 `fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c`,
20,243,600 bytes, regular, single link, mode 0755, nofollow attachment. It
copies those captured bytes once with `O_EXCL|O_NOFOLLOW` into the sparse
snapshot **as mode 0400**, verifies the copy by another held read, and adds
one repository-relative native row only to the later Mapper selection. The
closed Mapper manifest therefore contains 1,762 selected input rows: the
Reader closure, its manifest, four delayed Mapper roles, and the native row.
The generated read bridge resolves that one row only from the read-only
snapshot, with exact digest and non-executable mode. It does not turn the
native path into an executable command.

The original 27-role plan remains prospective. The controller exclusively
materializes four Mapper role leaves and one Mapper manifest after held
Source/package/Reader predecessor checks. A third read-only Bubblewrap child
imports generated `mapped.base` and calls only `base.verify_source(pin)`;
`mapped.build`, native dispatch, Mapper package/receipts, and Context remain
outside this slice. Source/Reader family leaves must match before and after,
and scratch cleanup is observed. The same 180-second child caps, 900-second
effect/capture watchdog, held evidence-directory cooperative lock, bounded
diagnostics, process-group closure, and no-replace numbered publication apply.
The child envelope uses Linux `waitid(WNOWAIT)` to hold the session leader's
PID after exit while it observes live members of its process group through
`/proc`. It may signal that group only while the held leader anchors its
identity. A surviving descendant after ordinary leader exit is killed under
a bounded grace/drain period, recorded as forced group cleanup, and cannot
produce a PASS even when the leader exited zero. The leader is reaped only
after no live group members remain; final process-group absence is then
observed. A cleanup or observation failure refuses success.
If `/proc` inspection or a cleanup signal handler fails, an outer cleanup
path retries an anchored SIGKILL while the leader is still held. It reaps
only after a live-member scan is empty. If repeated failures leave live or
unknown members, it retains the scratch and the in-process leader reference,
stops later phases, and records a sanitized FAIL receipt with
`scratch_cleanup_observed=false` and `scratch_retained_unknown=true`. A child that
closes its output pipes remains under the original monotonic child deadline;
it cannot gain a fresh cleanup interval to execute. The group-drain timer
starts after leader exit or forced cutoff, separately from execution time.
An attempted launch without proven reap and post-reap group absence also
retains scratch. In-process retention cannot guarantee custody if the
controller itself exits; no closure claim is made on that path.
The CLI now exits nonzero when it publishes a FAIL receipt; publication
success itself is never interpreted as fixture success.

The prospective effect entrypoint is
`PYTHONPATH=implementation/lab-runtime/candidates/runtime-completion-0001 python3 -m t35_external_v1.phase_scoped_v2.mapper_readonly_0002`.
This file and its tests establish an inactive construction candidate until
an independent exact-byte static review and a separately controlled one-run
attempt. A future PASS would be disposable import/selection evidence only.
Both PASS and FAIL receipts set `containment_scope` to
`observed_process_groups_only` and `escaped_session_absence_proven` to
`false`. A descendant that calls `setsid` and escapes the process group is
outside this fixture oracle. Protected host containment still requires the
LC-U03-02 cgroup oracle and actual dedicated-UID deployment evidence.
There is no protected issuer, actual WSL host qualification, unit acceptance,
installed service controller, native Mapper construction, or activation.
