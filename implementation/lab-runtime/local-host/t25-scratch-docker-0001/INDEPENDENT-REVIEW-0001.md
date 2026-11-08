# Independent scratch Docker review

Reviewed exact bytes on 2026-10-24, without changing the active runner:

- `build_context.py`: SHA-256 `94cfaa0e0d63a815f74d3d5f3246ee428cfde87c415b0dc8653120a5bf346ddb`
- `run_qualification.py`: SHA-256 `a8c4567b96cb171ef79bc192562f0f54bb4a82afd5f9a97053963eb3cdf4d2ab`

No demonstrated blocking code defect found in this read review. Actual Docker
installation and API qualification remain separate evidence. This review does
not claim the ongoing Docker process has completed.

The six copied controllers cover the actual import graph:
`install_from_archive` imports `archive` (which imports `materialize`),
`native_install`, `configure_installation`, and `construction_runner`.
Controller, host snapshot, archive, and public native bootstrap bytes are copied
against independently selected package digests. The installer independently
validates archive membership and performs a fresh private native installation.
The bootstrap is correctly excluded from installed-runtime attestation.

The controlled UID/HOME and volume retain private installation state outside
the read-only image. Snapshot ownership permits the unprivileged process to
read the selected inputs while read-only root prevents changes. Network is
disabled, all capabilities are dropped, no-new-privileges is requested, and the
root filesystem is read-only. Unique random resource names constrain cleanup
to this invocation. Failed execution deliberately retains its owned resources;
the resource manifest identifies them. No broad Docker prune occurs.

Two small follow-ups remain for a successor after the current run terminates:

1. The result asserts `no_new_privileges: true`, but the inspection predicate
   does not verify `HostConfig.SecurityOpt` contains `no-new-privileges:true`.
   Verify the actual state before asserting it, as for read-only root and caps.
2. Successful-run cleanup is outside the failure-recording `try` block. A
   partial cleanup failure retains `OWNED-RESOURCES.json` but produces no
   `FAILED-RETAINED.json` describing which removals succeeded. Record that
   partial state without claiming complete cleanup or deleting unrelated data.

No selected code was modified, no runtime callback was replaced, and no private
installation contents were read as part of this review.
