# Lab Operational Runtime/v2 candidate

This source-profile successor retains D75 admissions and explicitly selects the later specialist-owner-bootstrap-0003 Project State. The v1 implementation remains admitted by D75 and byte-exact; this v2 executable is a candidate for owner review. See the [4 November source-profile repair](SOURCE-PROFILE-REPAIR.md).

[Review and example](REVIEW.md) · [Exact profile](profile.json) · [Interface contract](CONTRACT.md) · [v1 admission](../ADMISSION.md)

## Inspect the current foundation

From repository root with Python and the dependencies in `requirements.txt`:

```bash
python3 implementation/lab-runtime/v2/lab.py status
python3 implementation/lab-runtime/v2/lab.py verify
python3 implementation/lab-runtime/v2/lab.py inspect implementation:cyberalchemy-lab:operational-runtime:v1 --record
python3 implementation/lab-runtime/v2/lab.py query Lifecycle
python3 implementation/lab-runtime/v2/lab.py catalog --category definition --current
```

Reads need no initialized store. They select the current specialist-owner State and both history cursors at 7, retain D75's exact admissions and historical predecessors, and verify the generated current-state lookup against the explicitly pinned successor bundle. Each successor must extend the exact predecessor State and history and match its application receipt. Definitions, Artifact Types and Relation Kinds still use D74's unchanged registry anchors. Native bootstrap roles and assignments are retained source evidence; this adapter projects only their State/history checkpoints and grants no native role authority. Queries expose unresolved earlier references and traversal limits.

## Local branches and explicit approvals

The CLI and six protocol schemas retain the v1 interfaces described in [the v1 operator guide](../v1/README.md). Use the v2 executable path in each command. Its default store is `.local/lab-runtime/v2/store`; choose an explicit separate `--store PATH` before each command when needed. Private keys stay outside the repository and store.

Initialize a fresh branch with an explicitly provisioned owner/public key. The branch freezes this exact profile and source snapshot. Old-profile stores remain inspectable as stale; review, authorization, apply and Agent context require the active exact profile. Recovery preserves a branch's committed history and does not rebase it.

One exact signed local approval can cover independent targets and their deterministic State/history/registry/governance/relation consequences. The first transaction from this baseline would advance both history cursors from 7 to 8 inside that local branch. It creates no repository Decision.

Agent context is reconstructed from the selected Project State and bounded ontology projection. Short memory belongs to the process session, expires, and is erased on close. A durable lesson or outcome requires an explicit schema-backed local transaction.

## Repeatable validation

```bash
python3 implementation/lab-runtime/v2/validate.py --workers 6 --write-receipt
python3 implementation/lab-runtime/v2/demo.py
```

With multiple workers, each check runs in a separate process with its own temporary store and keys. The complete discovered suite is recorded, including failures.

The suite retains D75 record and connection checks, historical revisions and distinct package labels, older-profile store rejection, initialization profile compatibility, and current-State lookup drift. Successor checks cover exact ancestry/history extension, receipt bindings, changed source refusal and the native-role projection boundary. The demonstration performs one authorized local Work transaction, fresh-process replay, idempotent repeat and ephemeral context preparation/closure in a disposable branch. Writes never change repository authority.

The [validation receipt](receipts/validation.json) binds actual outcomes to exact candidate bytes. Its claim is limited to local process interruption and this filesystem; no power-loss, multi-host or external execution claim follows. The v1 validation receipt remains bound to its original reviewed bytes.
