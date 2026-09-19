# Produce Verified Patch Candidate imported

Existing invariants and interface requirements -> explicit input bindings -> candidate import.

This Capability describes producing a patch candidate for one bounded fixture request. The model proposes; a separate exact-action approval precedes any mutation, and a separate verifier must check the result. Importing the Capability runs none of those operations.

The missing acceptance field now contains five source ontology invariants and nine interface preconditions. They cover proposal-only model sessions, untrusted model output, exact action approval, no blind retry after ambiguous effects, and independent postimage verification.

Two missing input identities are now explicitly bound as local candidates:

- `CA2-CONTRACT-CODING-REQUEST` uses a closed schema derived from the authored CodingRequest model's run ID, request and base-tree digest, with no authority effect.
- `CA2-CONTRACT-NEXT-ACTION-CANDIDATE` reuses the existing source schema byte-for-byte in JSON meaning. Its source identity is preserved; the local binding does not rename or admit it.

The output contract resolves to the existing interface contract. [result.json](result.json) records the original source, mappings and remaining candidate dependencies. [imports.json](imports.json) preserves the prior 25 imports and adds this candidate to `.local/capability-inventory-import-0013/imports.json`.

Seven import checks passed: deterministic replay, missing invariant rejection, wrong output rejection, missing precondition rejection, valid/hostile schema fixtures for both input contracts, and store/report equality. The combined graph validates. [verification.json](verification.json) binds the run. No model was invoked, no patch was executed, and source runtime product tests were not rerun. Schema validity is not approval, allowlist enforcement, verification success or operational admission.

Current queue: **26 imported candidates / 19 blocked declarations**. Next is Control Continuous Construction Task Loop.
