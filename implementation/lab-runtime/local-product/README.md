# Local Work product journey

From the repository root, run:

```bash
python3 implementation/lab-runtime/local-product/run.py
```

Use `--json` for the complete machine-readable receipt. Python needs the
packages listed in [`../v1/requirements.txt`](../v1/requirements.txt).

The launcher uses the admitted operational runtime v1 and its exact D74 source
profile. In a new disposable directory outside Git, it creates a fixture owner
key and local store, reviews one planned Work record, verifies that an altered
proposal is refused under its original signature without advancing HEAD, then applies the correctly signed
transaction. It checks exact retry, fresh-process replay, and an ephemeral Agent
context whose short note is erased on close. The directory, key, and store are
removed before the command reports success.

This is a locally runnable product journey on actual repository source bytes
with fixture authority over its own temporary store. It changes no repository
admission, provisions no persistent operator identity, and performs no
deployment or external effect. The v1 profile reports D74 even though the
repository's current Project State is D75. The larger runtime-completion plan,
its 34-operation API, and actual owner/host qualification remain separate work.
