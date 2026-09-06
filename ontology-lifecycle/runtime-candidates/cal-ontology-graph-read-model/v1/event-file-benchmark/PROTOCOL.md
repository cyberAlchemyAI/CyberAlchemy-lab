# Generated event-file recovery protocol

For each selected profile, the harness performs this sequence:

1. Build the locked fixture generator and recovery CLI outside the timed region.
2. Generate temporary canonical-format semantic and governance files.
3. Independently calculate the expected source envelope and graph index in the generator.
4. Start two independent recovery processes over the unchanged files.
5. Record wall-process, event-store load, and graph-rebuild time.
6. Compare the normalized recovery receipts and exact expected digests.
7. Add leading whitespace to the first semantic event and require
   `NON_CANONICAL_JSON` from a separate control process.
8. Delete the temporary fixture with the harness-owned temporary directory.

Compilation and fixture generation are reported but excluded from recovery
timing. Every saved result declares `canonical_replay_source: false` and
`authority_effect: none` because the graph model is disposable and the fixture
has no product authority.
