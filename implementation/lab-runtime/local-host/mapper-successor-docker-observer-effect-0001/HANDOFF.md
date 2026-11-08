# Mapper external observer one-shot wrapper 0001

Status: **effect-enabled source, UNRUN, awaiting independent static review**.
Do not dispatch before that review. This wrapper selects frozen observer0002
SHA-256 `356a3abd41a28a3400f22f8e1aac35f33e7176893090c3a27783cd51b99b4a07`
and independent PASS review SHA-256
`a76d0fd9245dcce50e362df0f087a2658c1d243c691b085f0176b6b60100ab0b`.
Observer source SHA-256 is
`119ee270ddf26bd00ecfad18752d0380601aca362966bd5f70ed2623930ebbe4`.
The reviewed observer in turn pins the exact Mapper release freeze/review.

Read-only preflight command:

```
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/mapper-successor-docker-observer-effect-0001/wrapper.py --preflight
```

The **only future one-shot effect command** is:

```
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/mapper-successor-docker-observer-effect-0001/wrapper.py --execute-reviewed-one-shot
```

`load_reviewed_observer()` nofollow-reads this wrapper's freeze/members and
the predecessor's freeze, review and three members. It checks owner, mode,
size, inode identity and hashes, then compiles the exact captured observer
source buffer once into an in-memory module. Dispatch passes that same
module's `preflight` directly to its `_run_once`; there is no second pathname
import or swapped observer body. The observer preflight rechecks the release's
selected attempt/name and absence state immediately before its exclusive
observation claim. Its owner-0700 consumed marker and fsynced intent precede
the exact release process spawn. Raw stdout/stderr and strict OS exit remain
under the observer's owner-0600/no-retry protocol.

The wrapper returns only `PROVISIONAL_OS_ZERO_FINAL_JOIN`. It does not mark
Mapper output accepted, issue Context authority, or certify the original
protected Source8 task. External OS exit, terminal/package/CID/name absence,
raw hashes and independent effect review remain required. The real
observation root and Mapper attempt must remain absent before dispatch. No
effect or private archive body read occurred in preparing this wrapper.

Six inert tests pass in normal Python and `-O`: exact source loading,
preflight redaction, one-loader/one-call dispatch, disabled-gate refusal,
UNKNOWN refusal and digest drift. They never call the real `_run_once` effect.
An independent reviewer should rehash this freeze, rerun read-only preflight,
and challenge the compiled-buffer identity, one-shot handoff and no-retry
selection before authorizing the exact command above.
