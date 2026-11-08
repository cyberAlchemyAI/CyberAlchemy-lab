# Actual Service and Vault interruption probe

`probe.py` runs the selected API's real Source replay, schema registry, independent metadata Reader policy, nonce authentication, Service, and common dispatcher. The maintained metadata fixture must support the selected current family. The parent and children own fresh private `/tmp` roots and never replace a production callback or clock.

For each of two fresh cases, the parent installs a Linux inotify observer before starting `change.prepare`. It observes the actual Vault claim or completed-result publication, stops the process group, confirms the requested boundary still exists, and sends SIGKILL. A missed claim-before-result window fails the probe. This tests process interruption and filesystem readback, not host power loss or storage hardware guarantees.

A new native child authenticates to the same independently pinned policy, proves its reconstructed request has the same control fingerprint, and calls the same common dispatcher. A pending claim must return `recovery-required`; a recorded result must be read without changing durable bytes. Changed control inputs under the same key must return `idempotency-conflict`, also without changing those bytes. An unrelated sibling is preserved. Successful cases remove their owned temporary roots; failed cases retain the actual private journal and a `FAILED-RETAINED.json` marker for inspection.

Use the exact selected installed launcher with `--launcher`, or a separately verified bundled installation with `--native-root`; supply `--api`, `--source-sha256`, `--profile-sha256`, `--deps` and a new `--output` path. The child flags are orchestration-only, outside the API wire protocol. The exclusive output is written only after both actual cases and cleanup pass. Failed runs retain their command log and private case root, and are not successful receipts.

No actual execution has yet qualified this runner. It does not by itself cover the workflow journal, Machine transport, hostile-input matrix, or complete T18.
