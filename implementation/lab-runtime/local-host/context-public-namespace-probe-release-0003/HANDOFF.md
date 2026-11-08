# Context public-only namespace probe release 0003

Status: **effect disabled, UNRUN, awaiting independent static review**. This is
a fresh disposable public probe after the consumed 0002 attempt. The 0002
attempt and all of its external and inner observation roots remain retained
and must never be retried or reset. Its structured independent effect audit
SHA-256 is `839aeca6fc3d7c61b3affd4b452af185c13e920544bc6bbc4f650223f82d9640`
(review text SHA-256
`31e081d42b94870a0f028dcf0630a6e4655eba3a04c06ee505496e6c4a43f03f`).
The audit found a pre-Docker `DIR_MODE_OR_OWNER` refusal on a newly created
0700 stage directory when the code requested 0755. An inherited 0077 umask
reproduces that exact failure; the historical umask was not recorded. No
Docker create/start or namespace handshake occurred in the failed attempt.

This successor selects fresh identities:

- Attempt: `/home/vlad_/.local/state/cyberalchemy-lab/context-public-only-probe-20261020-0003`
- Observation: `/home/vlad_/.local/state/cyberalchemy-lab-observations/context-public-only-probe-20261020-0003`
- Docker name: `cal-context-public-only-probe-20261020-0003`

The new `Attempt.mkdir` first proves a held nofollow child directory's owner
and attachment. Only if this call exclusively created the directory does it
apply `fchmod` to the exact selected mode, fsync the child, and read back the
mode and identity before staging content. Existing directories are verified
but never chmodded. A failure after opening the child closes its descriptor;
ownership of each parent FD transfers before ambiguous close. The inner
observer now classifies failed release OS exit or stderr before parsing stdout,
preserving the direct refusal instead of a secondary empty-JSON error.

The five exact child binds remain read-only at `/workspace`, `/control`,
`/runner`, `/cache-disabled`, and
`/attempt/input/lab-context-native-reader`; there is no nested writable
workspace, private source, key, grant, policy, actual Context role, or
protected archive access. The disposable public child still proves VFS
mountinfo `ro`, EROFS30, READY/GO/ACK and post-ACK parent Writer visibility
only if a later independently reviewed one-shot effect succeeds. The current
candidate establishes none of those runtime observations.

Read-only preflight, already run successfully for these new absent identities:

```
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/context-public-namespace-probe-release-0003/release.py --preflight
```

Normal Python and `-O` each pass 13 public-fixture tests. New causal tests
reproduce predecessor failure under umask0077 and prove successor exact0755,
reject an existing wrong-mode entry without chmod, close a child descriptor
after injected post-open failure, and retain direct failed-release exit
reason with empty stdout. No Docker create/start, private body read, or actual
probe effect was performed. Independent static review should rehash the
freeze, verify fresh names and absence, challenge mode/FD custody and the
observer correction, and require a separate exact external one-shot wrapper
review before dispatch.
