# Independent installed regression harness review

PASS for the corrected reporting and process-custody harness; actual execution of the complete maintained suite remains pending. Reviewed all coordinator/worker paths, the pinned 21-class/345-method inventory, selected bootstrap/original-byte loader, whole-class setup/teardown, terminal row accounting, entry/exit guards, actual event-log hashes and exclusive result files.

Two findings were resolved. First, passing method rows could erase a teardown/exit-guard failure in the coordinator's final result. Acceptance now additionally requires every worker to report PASS with zero process exit, no timeout, complete exact method identities/counts, both guards, no fixture/execution error and all methods executed. The final coordinator requires every bucket to pass. Skips, expected failures, setup failures and unrun cases never count as passes. Second, a timed-out worker could leave its native children behind. Each worker now owns a separate process group; timeout/error cleanup signals that group only.

Independently reran six causal accounting/process-custody tests normally and with optimization: complete/unrun accounting; teardown/exit failures despite passing methods; nonzero exit/timeout after a PASS file; duplicate/changed IDs; missing bootstrap; actual worker/grandchild timeout with an unrelated process preserved. All passed. These small tests do not execute or qualify the real 345-method suite.

Selected coordinator: `00bfcf9117baf441dc52cafd920702aa9fc9b3966a352dc01d3b9dd60dced257`.
Selected worker: `79b9d60b91d0688616d8a890e0a566a090dab959666826e95efdeb8d5fd43a8a`.
