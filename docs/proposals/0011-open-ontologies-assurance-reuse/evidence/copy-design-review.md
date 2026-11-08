# Source-copy design review

Verdict: PASS WITH IMPLEMENTATION GATES. No blocking defect found in the reviewed copy choices or illustrative batch interface. This is a review of the proposed source selection and its stated boundaries, not a successful import, build, runtime test, proof check, or license-exception clearance.

## Reviewed artifacts

In docs/proposals/0011-open-ontologies-assurance-reuse/:

- UPSTREAM-COPY-MANIFEST.json
- CODE-REUSE.md
- examples/preserve-batch.json
- DELIVERY-LAYERS.md

Reviewed SHA-256 identities:

| Artifact | SHA-256 |
| --- | --- |
| UPSTREAM-COPY-MANIFEST.json | 2db481d59bfa680385c28e8284bd4df1686e308dc5c47b34a067f7db1b157c65 |
| CODE-REUSE.md | 843cac1f7634d8e9611b08fdb16fd8d9d9f158c006de26df164245c41039ca9f |
| examples/preserve-batch.json | 5ea577ed43681a43a88094f77dc8b8bfeb5502fd4088a40391eb14cb260feb6e |
| DELIVERY-LAYERS.md | 2441824cf51e9a5906b191e45e5c7b2de793601e89cab8d7bc35dbf460808572 |

Compared against upstream clone /tmp/cal-open-ontologies.ANeAQC/repo at commit c7fd75f9491253c56e4d4f408ceac179de343e48 and tree cff967fe9d6fe8032b8dc501c461ac1c916b280d.

## Source identity and file closure

I independently checked all 597 manifest entries:

- 597 distinct upstream paths and 597 distinct destination paths.
- All files exist in the clone.
- Every declared byte length and SHA-256 matches actual file bytes.
- Every Git blob ID matches the Git blob hash of those bytes.
- Every declared Git mode, object kind and blob identity matches git ls-tree.
- Total size is 9,570,058 bytes, matching planned_bytes.
- All 597 entries have planned-not-copied status.
- None of the 597 intended destination paths currently exists in the Lab.

Tracked-source closure checks match the complete selected units:

| Root | Upstream tracked files | Selected files |
| --- | --- | --- |
| src/ | 107 | 107 |
| .cargo/ | 2 | 2 |
| lean/ | 84 | 84 |
| isabelle/ | 104 | 104 |
| rocq/ | 18 | 18 |
| tests/fixtures/horn/ | 18 | 18 |
| tests/fixtures/folmodel/ | 11 | 11 |

The manifest's grouped counts also agree:114 root Rust/package/config files,2 CI reference files,1 MIT notice,122 later independent-workspace files,84 Lean files,245 Rust test/helper source files and29 initial fixtures.

The complete standalone Rust source unit contains Cargo.toml, Cargo.lock, all root src files and .cargo settings. No missing compile-time include_str/include_bytes dependency outside that selected source was identified. Runtime checkers, libraries resolved by Cargo and external test assets are separate dependencies; this static check does not prove the crate builds.

## Build-unit decision

CODE-REUSE.md:29-48 correctly keeps the engine as its own Cargo root, preserving the root patch.crates-io for Oxigraph revision37db8e1522585ed2f9aa994be6c5c716859af5c8. This avoids accidentally losing the patch by making the upstream crate a dependency of a different workspace. It also retains the original lock and default empty optional-feature set.

The document correctly treats compiler/target selection and actual binary builds as future gates. It does not claim that copying Cargo.lock makes an unpinned Rust compiler or all dependency retrieval reproducible. Lean build caches are excluded and selected compiler/checker outputs must be rebuilt. Retained optional Isabelle/Rocq units are explicitly L4, not a required L0 launch.

## Test and fixture scope

The design deliberately retains245 Rust test/helper source files but initially selects only Horn and finite-model fixture groups. Many other retained tests reference omitted standards/data/model/prover assets.

This is acceptable because:

- The manifest test_execution_policy explicitly limits runs to selected targets with reviewed fixture/tool closure.
- CODE-REUSE.md:14,68-78 says tests do not implicitly select external datasets and retained test sources do not imply runnable or passing full-suite coverage.
- DELIVERY-LAYERS.md:18-21 separates retained code from activated capabilities and assumes no proof/performance result.
- tests/common/mod.rs is present for fixture-skip strictness and fork/exec coordination helpers.

Implementation must not turn this into a generic cargo test --all-targets green-coverage claim. Before running a selected test, list its local fixture paths and external binaries, verify their exact identities and required skip policy, and record actual discovered/passed/failed/skipped outcomes. Some retained tests may fail to compile without omitted include-time fixtures; that is a reason to choose an explicit closure, not to silently edit or remove the assertion.

## Licensing and excluded data

The exact upstream MIT notice is included with its matching digest. CODE-REUSE.md:65-74 retains in-file notices, excludes broad corpora and standards suites, and requires a per-unit exception scan before actual copying.

The selected files do not silently pull in benchmark, case-study, data, demo, model or standards-suite directories. Retaining test code that refers to such directories is explicitly distinguished from retaining those assets.

The exception scan remains a real import gate: root MIT is not blanket authorization for every repository dataset. Known examples include W3C suite licenses, the Apache-2.0 OntoAxiom benchmark, CC-BY4/OGL source crosswalk material and separately licensed case-study artifacts. Since these asset groups are excluded, no new broad dataset-copy requirement is created by this manifest.

## Batch interface example

examples/preserve-batch.json is valid JSON and uses the actual upstream supported positional-array form:

- load receives its source file as one literal positional argument.
- preserve receives separate --projection, --goals, --profile, --out, --checker and --require-checker arguments.
- Paths are illustrative owned-job and pinned-build paths; they are not a claim that these paths or the worker exist.

The upstream parser at src/batch.rs:1607-1647 accepts these arrays. preserve's implementation reads these named options, and --checker/--require-checker are part of its actual options. This avoids the object-argument pitfall where a path becomes a --path flag.

The separate process adapter must still invoke the binary with --no-connect, a unique --data-dir, JSON output and the chosen batch failure policy; the JSON file itself supplies only the commands. It must allowlist commands, inspect every result and final exit status, and refuse missing checker or incomplete/unknown evidence under the selected profile. This review did not execute the example or check a preservation theorem.

## Implementation gates retained

1. Per-file notice/exception review and actual source/destination copy receipt.
2. Exact Rust/Cargo/platform and Lean toolchain selection; preserved store fork/lock; selected successful builds and binary hashes.
3. Explicit chosen upstream test targets with full local-fixture and external-tool closure; strict skipped-fixture accounting.
4. Worker adapter with no daemon auto-connect, no live service or external mutation commands, per-job state and complete raw/parsed result accounting.
5. Lab-specific exact-cut RDF/goal translation and independent meaning/profile/unsupported-field checks.
6. Separate acceptance of any stronger profile, optional feature or later prover workspace.

No canonical artifact was edited by this reviewer. No implementation or full upstream-suite coverage occurred as part of this review.
