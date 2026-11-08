# Historical Mapper read-only replay effect candidate 0003

Status: **inactive, unreviewed effect candidate**. Import and synthetic tests
perform no Bubblewrap or native effect. `historical_mapper_replay_effect_0003.py`
has a deliberately explicit `run_and_publish()`/CLI effect entry point; do not
invoke it until independent exact-byte static review and a no-replace
preflight permit one attempt. No attempt or result name has been published.
V3 reserves separate no-replace `historical-mapper-replay-attempt-0003.json`
and `historical-mapper-replay-result-0003.json` names; the v1/v2 names remain
unused historical design slots.

This controller consumes the exact 55-leaf checked-in historical package and
five selected runtime leaves pinned by `historical_mapper_replay_0001.py`.
Under an evidence-root `flock`, it refuses an existing attempt, result, or
retained result temp. It chooses the scratch name before writing a durable
mode-0600 no-replace attempt marker, so that marker binds the exact 37-token
native argv digest, version argv digest, selected package inventory/runtime
hashes, controller/plan/custody/test code hashes, limits, and result name.
The marker is retained on success or failure. If publication fails or the
process crashes, this name is spent; do not run the same effect again.

Only after the marker is durable does the controller create one private owned
scratch root. It makes held, nofollow byte copies of the selected five runtime
leaves and 55 package leaves, verifies the whole source package again, and
holds/rehashes all 60 scratch leaves before and after each child. Package
leaves are 0400 and directories 0500; the selected Bubblewrap, ELF, and loader
copies are 0500, while ABI libraries are 0400. It runs one bounded version
child, then two fresh native processes with the same exact five-read-only-mount
argv. Each native child has a 30-second monotonic deadline, a 262,144-byte
stdout cap, and a 256-byte stderr cap; the aggregate watchdog is 90 seconds.
It requires both outputs to equal the historical output bytes by size and
SHA-256 and to equal one another. Standard error must be empty, exits zero,
and original process groups fully observed closed with no forced cleanup.

The controller inherits the independently exercised v5 smoke's held-path,
process-group closure, evidence-root lock, and no-replace publication helpers,
pinning their exact source hashes. It restores scratch-directory owner-write
mode through renewed held identities only after observed child closure, then
removes owned scratch. If child closure or directory custody is unknown, it
retains scratch and records a sanitized FAIL. The final receipt is written
through a mode-0600 exclusive temp, no-replace hard link, fsync, and readback;
it contains hashes/lengths/closure flags, never raw package or child output.
Original-group observation cannot prove absence of escaped sessions.

V2 repaired the independent 0001 HOLD: once `Popen` returns, every selector
shutdown, output-bookkeeping, and stream-close exception is recorded as a
failure but still reaches original-group closure in a separate cleanup path.
The controller forces closure on an observation error, holds the leader until
the group is checked, and only then re-raises the original failure. Synthetic
fault tests inject each post-launch failure against a sleeping Python child;
they check observed reaping and conservative scratch retention if closure is
itself uncertain. V1 remains historical and must not be used for effect.

V3 repairs the independent 0002 adversarial HOLD. The aggregate `SIGALRM`
is blocked before `Popen` and stays blocked throughout observation, selector
shutdown, output bookkeeping, stream close, `close_group`, original-group
absence observation, and leader reap. The controller polls pending alarm state
at the observation loop and cleanup boundaries; a pending alarm forces a
bounded group cleanup and FAIL. If it arrives inside `close_group`, that helper
still has the 30-second child deadline plus bounded kill/reap waits. Only
after closure does v3 restore the prior signal mask, permitting the watchdog
handler to raise. Synthetic tests deliver a real process-directed `SIGALRM`
at selector cleanup entry and during output bookkeeping; both observe the
handler only after `reaped_observed` and `group_absent_observed` become true.
V1 and V2 remain historical; neither is eligible for an effect preflight.

Even a future PASS would be a historical checked-in 25-event native read-only
diagnostic. It would not establish a fresh same-scratch Mapper package,
protected Source8 authority, Context, LC-U03-02 host containment,
LC-U02-05 acceptance, or activation.
