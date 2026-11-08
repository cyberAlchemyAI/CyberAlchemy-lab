# Source-only Docker controller 0006

Status: **HOLD_EFFECT_PENDING_INDEPENDENT_REREVIEW**. The frozen 0005 static
review reproduced SOD-R05: case-folding the entire Docker inspect diagnostic
made an uppercased *different object name* appear equal to the selected
lowercase name. Preserve 0005 HOLD and all predecessor bytes. No Docker Source
effect ran in this version.

This disjoint controller selects the unique name
`cal-source-only-20261020-0001-0006`. On a failed Docker inspect, it accepts
absence only when exit code is exactly 1, stdout is `[]` or empty, and the
**whole** stderr matches the pinned CLI's not-found diagnostic. Only the human
prefix (`error: no such object:` or `error: no such container:`) is matched
case-insensitively with separator whitespace variation. The object-name bytes
must equal the selected name exactly. Wrong-case and wrong-name objects,
embedded not-found substrings, transport errors, wrong exit codes and partial
stdout are ambiguous. Required absence observations are repeated.

`static-normal.log` and `static-optimized.log` each show 28/28 PASS. The
causal negatives now include fully uppercase and mixed-case wrong object
names, while uppercase diagnostic *prefix* with the exact selected name is a
positive. The inherited fake-daemon, signal, cleanup, durable pre-removal and
nonregular-output tests still pass. A read-only live-daemon `docker inspect`
for the 0006 name also passed in both modes. `stage-check.stdout` records a
separate read-only PASS for the actual 941-file stage, fresh output roots,
selected host binaries, current episode and absent 0006 container. None of
these checks creates or starts a container or reads a historical protected
`branch.snapshot` body.

The proposed Source effect command, **not executed**, is:

```bash
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/source-only-docker-0006/controller.py --execute-reviewed-one-shot
```

The cleanup-only command after a consumed attempt is:

```bash
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/source-only-docker-0006/controller.py --recover-consumed-cleanup
```

Independent static rereview and a same-state pre-dispatch audit must bind this
freeze, the exact 0002 public cut, selected stage, host binaries/image, absent
marker/CID/log/terminal/recovery names, current episode and Docker name before
one dispatch. The episode expires 2026-10-21 08:20 UTC. A successful effect
could claim only a new disposable local Source package and signed cold replay,
not Reader/Mapper/Context, protected Source8, host qualification or original
36-task acceptance.
