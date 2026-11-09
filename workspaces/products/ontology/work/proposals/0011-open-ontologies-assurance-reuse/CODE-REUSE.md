# Copy whole reusable units, write small adapters

The selected policy is to copy unchanged implementations first. New code is
limited to Lab-specific translation, proof assembly, invocation and evidence
accounting. Copy volume is not a reason to weaken a source meaning.

## Copy and reuse decisions

| Unit | Selected action | New work |
| --- | --- | --- |
| Entire upstream `lean/` | Byte-identical copy, including Lake/toolchain metadata; 84 files, 1,136,038 bytes. | Build provenance, restricted exporter, semantic bridge and concrete proof module generator. |
| Root Rust `src/`, Cargo manifests/lock, `.cargo/` and package context | Byte-identical standalone source/build unit. | Narrow Python subprocess adapter over existing JSON batch. |
| Root MIT notice | Retain alongside every copied source unit. | Copy receipt and notice accounting. |
| Upstream test source and `tests/common/` | Copy original code, retain relative layout. | Select runnable targets with their full fixture/tool closure. |
| `tests/fixtures/folmodel/` and `horn/` | Copy complete good/bad fixture groups unchanged. | Lab bridge mutation cases and explicit expected outcomes. |
| CI source | Retain as reference; adapt in a separate Lab workflow. | Correct working directories, strict tool checks and manifest-bound caches. |
| Isabelle and Rocq Horn workspaces | Whole-unit copy in later L4 only. | Optional toolchains and profile-specific cross-check reports. |
| Existing Lab definition assurance | Reuse capture, typed IR, required-set generation, finite search, invalidation and bundle discipline. | A new provider contract and evidence decoder; do not relabel old finite results. |
| Existing Lab supervision/proof-audit mechanics | Reviewed successor copy where APIs are fixed to their old owner. | Explicit ownership/import/schema adaptation and corresponding regressions. |
| Python Lite | Defer. It is another implementation, not required to call Rust from Python. | Consider only for a separately selected lightweight profile. |

The [upstream manifest](UPSTREAM-COPY-MANIFEST.json) gives every planned source
path, target, Git blob, byte length and SHA-256. The
[Lab baseline](LAB-REUSE-BASELINE.json) pins the actual inspected local files.
The [local copy decisions](LOCAL-COPY-DECISIONS.json) specify the supervisor and
resource-schema copy separately from unchanged calls into existing Lab code.
No listed runtime source has been copied by this design.

## Keep upstream build units intact

The engine is built as its own Cargo root with its original Cargo.lock and
`[patch.crates-io]`. That preserves Oxigraph revision
`37db8e1522585ed2f9aa994be6c5c716859af5c8`. A dependency's patch can be ignored
by a different workspace root, so importing the crate into a new workspace is
not the first implementation choice.

Use the original default optional-feature set: empty. No database connectors,
embeddings, WASM plugins or causal Python are enabled in the first provider.
Do not launch the MCP server, daemon or Studio. The narrow adapter calls the
existing batch path in a fresh process and keeps all engine state in its job.

The Lean workspace remains separate. Rebuild imported `.olean` and executable
outputs using the selected toolchain; do not copy someone else's build cache.
Preserve the complete default-target list and eventually build it all. First
delivery may build selected targets, but must report other targets as not run.

Rust compiler/target identity is not pinned by an upstream toolchain file.
Implementation must record an exact selected compiler, Cargo, platform, feature
set, lock resolution and output binaries. This is a build-readiness gap, not
permission to replace a dependency or edit its lock silently.

## Reusing our code has boundaries

The v3 supervisor currently requires a run root below its own tree. The extension
client accepts fixed E00–E06 profiles and their accepted receipts. They are not
generic extension slots. Copy the needed supervision primitives into the new
provider, adapt their imports/owned root, and freeze a new reviewed source
closure. Do not edit the old code or pretend its acceptance covers the copy.

The current definition verifier understands its finite witness contract and
rejects using a witness for a required universal proof. Keep that behavior.
The successor evidence accountant must explicitly recognize the new evidence
kinds and preserve minimum-strength rules.

## License and patch accounting

The engine code is MIT. Retain the exact notice and in-file notices. Exclude
benchmark/case-study corpora, downloaded ontologies, model weights, media and
vendored standards suites from the default selection. They can have separate
licenses. Selecting an upstream test does not implicitly select its external
dataset.

Before an actual copy, scan each selected unit for exceptions and bind the
result. Produce a receipt comparing source and destination bytes. Record any
later patch separately with base hash, patch hash, reason and tests. Upstream
style rewrites and namespace changes are unnecessary in the first import.

Code that is copied but not registered, built or exercised is reported as
retained source only. The copy manifest is not a statement that every retained
test has its datasets or passes.
