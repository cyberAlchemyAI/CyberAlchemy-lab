# Common workflow OS interruption caller review

Reviewed `t18-current-service-kill-0001/workflow_probe.py`, SHA-256
`c24b409e896ee26fdd182f9e3aeebf13971bdb40dc7494db7cba5dfbd4008bd0`.
The caller uses actual typed producer originals and an independently selected
private policy before each new Reader authentication. It does not replace a
Service/Source/clock/production writer. Fresh retry uses the same semantic
fingerprint and actual current Source, preserving outer pending state rather
than inventing a completed public result from an inner transaction.

Two review findings were repaired:

- The outer result is published by linking a completed fsynced temporary file,
  which emits IN_CREATE at its final path. Its observer now accepts that event.
  Inner claim/transaction files still require CLOSE_WRITE and HEAD requires its
  rename event, avoiding a stop during a partial direct write.
- Direct inner recovery now calls the actual installed OW.Selection guard with
  the original effective request deadline. Physical Source, API/schema, exact
  routing/method objects, current grant and deadline remain checked at recovery
  boundaries. The weaker producer-only callback is no longer used for recovery.

Independently exercised real Linux inotify events using direct writes, a
completed fsynced hardlink publication and HEAD replacement. The actual
production observer selector AST recognized each correct boundary. The old
selector would miss the hardlink result. Exact marker bytes were preserved.
Evidence is `INDEPENDENT-WORKFLOW-OS-PUBLICATION-0001.json`; this is a real OS
mechanics check, not a native Service interruption result.

Stopped-state JSON checks, missed-window refusal, process-group kill/cleanup,
failure custody, actual immutable transaction recovery, exact output-byte read
and unchanged outer pending journal remain intact. No additional blocker was
found in this bounded caller. Actual selected API calls and four interruption
episodes remain required. This does not qualify host power-loss durability.
