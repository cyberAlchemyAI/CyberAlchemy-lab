[Documentation home](../../README.md)

<a id="runtime-first-inspection"></a>

Lab runtime · proposed documentation

# First inspection without a store

Check the admitted v1 foundation and read one exact capability record.

Draft prepared on 2026-10-14. Integration and final T21 qualification remain pending.

<a id="runtime-first-inspection-result-and-prerequisites"></a>

<a id="runtime-first-inspection-result-and-prerequisites-title"></a>

## Result and prerequisites

You will verify the public v1 source selection, read its Project State and inspect one capability record. Use the existing selected installation0004 and repository root. This example does not install dependencies, initialize a store, create a key or call the integrated API.

The [actual parser](../../assets/43799f3efb2c-cli.py) has global options before its subcommand. The shell function below is defined in this page; it is a convenience around that parser, not an installed Lab SDK command. Its assertion refuses an existing store path before each invocation. Choose a fresh path rather than inspecting someone's existing local store.

<a id="runtime-first-inspection-run-the-three-reads"></a>

<a id="runtime-first-inspection-run-the-three-reads-title"></a>

## Run the three reads

````bash
# Run from the repository root, with the already selected installation0004.
lab_repository="$PWD"
lab_dependencies="$lab_repository/product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004"
lab_read_store="/tmp/cal-T21-read-$$"
lab_v1_read() {
  LC_ALL=C "$lab_dependencies/lib/abi/ld-linux-x86-64.so.2" \
    --inhibit-cache --library-path "$lab_dependencies/lib/abi" \
    "$lab_dependencies/bin/python" -I -X utf8 -B -S -c \
    'import sys,runpy;from pathlib import Path;assert not Path(sys.argv[3]).exists();sys.path.insert(0,sys.argv[1]);sys.path.insert(0,sys.argv[2]);sys.argv=sys.argv[4:];runpy.run_path(sys.argv[0],run_name="__main__")' \
    "$lab_dependencies/deps" "$lab_repository/implementation/lab-runtime/v1" \
    "$lab_read_store" "$lab_repository/implementation/lab-runtime/v1/lab.py" \
    --store "$lab_read_store" "$@"
}
lab_v1_read verify
lab_v1_read status
lab_v1_read inspect product-capability:cyberalchemy-lab:governed-knowledge-lifecycle --record
````

The independently selected interpreter/dependency closure is recorded in [dependency selection](../../assets/2345d4d3a59c-dependency-selection-0002.json) . Do not replace installation0004 with the newest-looking folder. The isolated flags avoid site-package and bytecode substitutions; the two explicit import roots are the selected dependency directory and v1's own directory.

<a id="runtime-first-inspection-read-the-observed-output"></a>

<a id="runtime-first-inspection-read-the-observed-output-title"></a>

## Read the observed output

The [14 October walkthrough](../../assets/555ad9970fcd-receipt.json) used the same parser/interpreter/import arrangement and a different deliberately absent path. verify returned PASS, 698 sources, 468 subjects and zero replayed transactions. status returned store_initialized: false, current freshness and repository_admission_as_of: decision:0074. The source snapshot digest was 3b7c0aa920c195d82b5c1dcc3652b28cd67554b5289f40cf546aa85a7ce3648e.

The capability inspection returned its exact record and separate axes. Effective status was admitted-current; the raw authoring status remained candidate-unadmitted, its domain lifecycle draft, and runtime realization not-observed. Explain each track separately. An admitted capability record does not establish that every implementation or consumer is currently running.

<a id="runtime-first-inspection-if-a-read-refuses"></a>

<a id="runtime-first-inspection-if-a-read-refuses-title"></a>

## If a read refuses

Stop on source drift, unresolved references or a dependency mismatch and preserve the selected command and public error. Do not initialize a store to hide drift. Read v1's [frozen profile](../../assets/7bf11e361cc9-profile.json) and [source capture](../../assets/7e9044d557b2-sources.py) .

The retained failed subject implementation:cyberalchemy-lab:operational-runtime:v1 is not a positive example. Its D75 admission is outside the selected D74 envelope. Read that admission through its original decision evidence or select a separately reviewed successor profile; do not edit the v1 profile in place.

No store should exist at the selected read path afterward. The [initial terminal](../../assets/83271e415731-initial-terminal.json) and [corrected inspection terminal](../../assets/bc30f73ec415-corrected-inspect-terminal.json) retain this scoped result. This is not a fresh-install or integrated-session walkthrough.

<a id="runtime-first-inspection-record-a-useful-reading-note"></a>

<a id="runtime-first-inspection-record-a-useful-reading-note-title"></a>

## Record a useful reading note

Write the executable version, cut, inspected identity, effective standing, raw authoring/domain fields, source digest and allowed conclusion. Link unresolved questions rather than guessing an implementation outcome. Continue with [architecture](../explanation/architecture.md) or the existing [provenance explanation](../../guide/provenance.md#evidence) .

<a id="runtime-first-inspection-sources"></a>

## Selected public evidence

- [docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json](../../assets/2345d4d3a59c-dependency-selection-0002.json). SHA-256 2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835; 317618 bytes. Public technical snapshot; no authority transfer.
- [docs/plans/0011-lab-runtime-completion/runs/0001-execution/T21/first-inspection-walkthrough-0001/corrected-inspect-terminal.json](../../assets/bc30f73ec415-corrected-inspect-terminal.json). SHA-256 bc30f73ec4150e25f38e52082d18d51572f7a7253c0ab194b11e58b099b6f850; 6611 bytes. Public technical snapshot; no authority transfer.
- [docs/plans/0011-lab-runtime-completion/runs/0001-execution/T21/first-inspection-walkthrough-0001/initial-terminal.json](../../assets/83271e415731-initial-terminal.json). SHA-256 83271e415731d0582fc14746ee72948c66a6f93c5ad44219d40e8806904b61d0; 12473 bytes. Public technical snapshot; no authority transfer.
- [docs/plans/0011-lab-runtime-completion/runs/0001-execution/T21/first-inspection-walkthrough-0001/receipt.json](../../assets/555ad9970fcd-receipt.json). SHA-256 555ad9970fcd382f54dbe354d3996523cc613524f9f71f5e1f966c34e3a38e51; 1879 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-runtime/v1/lab_runtime/cli.py](../../assets/43799f3efb2c-cli.py). SHA-256 43799f3efb2c53a4c9b39c99a681ecc7134182094aa06c14d66a378b594ba056; 11813 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-runtime/v1/profile.json](../../assets/7bf11e361cc9-profile.json). SHA-256 7bf11e361cc9d893dd809c28df464e66a8263ef0b14d48b1f34d0663dd2b2842; 5263 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-runtime/v1/lab_runtime/sources.py](../../assets/7e9044d557b2-sources.py). SHA-256 7e9044d557b2061223039bc15b74e84fc988c5cbd43c1cbd7401d67361ab8067; 16328 bytes. Public technical snapshot; no authority transfer.
