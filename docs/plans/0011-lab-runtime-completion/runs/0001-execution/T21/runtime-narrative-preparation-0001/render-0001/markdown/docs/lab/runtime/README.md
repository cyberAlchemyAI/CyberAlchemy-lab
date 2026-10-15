# Operate the Lab

Choose the implementation and the next task before relying on a runtime result.

Draft prepared on 2026-10-14. Integration and final T21 qualification remain pending.

## Start with the admitted inspection path

For a first inspection, use the admitted local v1 executable and its frozen Decision 0074 source profile. Decision 0075 admits that exact executable for local inspection, authorized local transactions, replay/recovery and ephemeral context. The admission is an external overlay: its original README can still say candidate without undoing the later decision. Read the [admission scope](../../../../../evidence/implementation/lab-runtime/ADMISSION.md), then follow [first inspection](tutorials/first-inspection.md).

The three-command walkthrough checks public source files and selects a deliberately nonexistent store. It creates no store, key or transaction. Its observed output is D74 with 698 verified sources and 468 subjects. This is a useful working entrypoint; it is separate from a permanent service, a new installation and the expanded API.

## Choose a surface

| Surface | What you can rely on | What remains separate |
| --- | --- | --- |
| Admitted runtime v1 | Exact local executable admitted by D75, reading its D74 profile | Current repository D75, permanent service and external consumers |
| Runtime v2 | Separate D75 source-profile candidate | Its candidate review does not replace v1 admission |
| API16 / composite catalog | Code and declared contracts for 28 Base, 3 Action and 3 Governance operations | Full current three-branch qualification and actual permission |
| Changed API17 | Reviewed overlay code exists | Old e417/5c capture is ineligible after changes; new family/selector/capture work is incomplete |
| Paperclip 2026.1005.0 | Recorded bounded process-reader episode | Live availability, a fresh grant, autonomous Work and human usefulness |

These surfaces have different stores, channels and evidence. A filename, result envelope or catalog count cannot select an authority boundary for you. The [dated status page](status.md) identifies the evidence cut.

## Choose your next task

| Your task | Reading route |
| --- | --- |
| Inspect a public record and explain its standing | [First inspection](tutorials/first-inspection.md) |
| Prepare a disposable local Work proposal | [Local Work](tutorials/local-work.md) and [provision and review](how-to/provision-and-review.md) |
| Understand agents and their limits | [Agent sessions](how-to/agent-sessions.md) |
| Deal with a timeout or pending effect | [Recover and retry](how-to/recover-and-retry.md) |
| Connect Paperclip to a selected reader | [Paperclip](how-to/paperclip.md) |
| Export, import or install a package | [Packages and installation](how-to/packages-and-installation.md) |
| Trace the code and state ownership | [Architecture](explanation/architecture.md) |

For meanings, use the existing [record and definition library](../../../../../../../../../../../lab/guide/records-and-connections.md) rather than treating these operational pages as replacement definitions.

## What a result establishes

Record the selected executable/profile, source cut, current permission, exact input and observed output. Then read the result posture. A prepared candidate, an admitted record, an actual action and an assessed benefit are distinct facts.

The full integrated learning path is not yet a supported successful tutorial. The measured episode expired, and the later family4 build exposed a dependency cycle before final runtime qualification. Those failures remain in [status](status.md) and [maintenance](development-and-maintenance.md). This handbook preparation does not close T21 or publish a release.

## Selected public evidence

- [implementation/lab-runtime/ADMISSION.md](../../../../../evidence/implementation/lab-runtime/ADMISSION.md). SHA-256 79c23e82b5dedb74b19580f845c333554e8cd5d73a5bd4e617d6879ebc341283; 1632 bytes. Public technical snapshot; no authority transfer.
