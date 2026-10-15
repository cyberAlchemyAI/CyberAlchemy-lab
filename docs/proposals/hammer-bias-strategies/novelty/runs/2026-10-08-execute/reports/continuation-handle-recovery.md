# Two saved outputs recovered after goal continuation

After the automatic goal continuation, native `collaboration.list_agents` lookups for `/root/h042_a` and `/root/h043_z` returned no agents. A full-tree lookup returned only the root. Both previously spawned attempts had saved output files. The latest goal continuation permits treating a missing native handle as stopped; file presence alone was not used for that determination.

The unchanged confirmation validator accepted the existing H042/A and H043/Z artifacts. The recovery operation recorded their hashes and joined them without regenerating, reconstructing or repairing their contents. No replacement role was spawned. Subsequent dependent roles received the same validated saved artifacts under the original frozen prompts.

Their terminal response messages were unavailable. The receipts explicitly set `native_terminal_response_observed: false` and `native_handle_missing_observed: true`, with a separate native-lookup witness. `join_status: completed` in these two receipts means a valid saved artifact joined after confirmed handle absence; it does not mean a terminal response was observed. This limit must remain visible in final execution accounting and the completion audit.

Evidence: [H042/A receipt](../receipts/H042-A.json), [its lookup witness](../receipts/H042-A-missing-handle-observation.json), [H043/Z receipt](../receipts/H043-Z.json), [its lookup witness](../receipts/H043-Z-missing-handle-observation.json), [recovery tool manifest](../native-handle-recovery-tool-manifest.json), [evidence bindings](../native-handle-recovery-evidence-manifest.json).
