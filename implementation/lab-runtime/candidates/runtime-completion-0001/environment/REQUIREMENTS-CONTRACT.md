# Original execution requirements adapter

`inspect_execution_requirements(raw, expected_sha256, prior_raw=..., repository=...)`
is a pure metadata validator. The caller supplies the current selected digest
independently, and it must equal the separately fixed full original revision-0002
selection digest `2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835`.
The prior original wheel/proof selection retains its fixed historical digest.
Coherently repinning the candidate descriptor, dependency selection and origin map
cannot omit or reorder any original input, exclusion, ABI or other requirement.
Alternative closures need a separate reviewed contract and cannot claim this
original closure's coverage. No member pathname in either document is opened, imported,
executed or promoted into a semantic Artifact.

The selected original T07 closure has 720 ordered input rows: eight wheels, one
interpreter, one native executable, 687 standard-library files and 23 ABI files.
The adapter retains the entire parsed original document, including order and
all original proof/exclusion/locator observations. It validates closed input
kinds, exact original wheel content, original executable content, module/root
destinations, complete native and wheel ELF metadata, transitive ABI references,
the inspection tool, package versions and the original seven-field R02 runtime
environment. Unknown fields and unresolved graph endpoints refuse. Candidate
metadata cannot replace the original source proof or prior wheel selection.

The source contract is `runtime-dependencies-v2-completion-0001/closure.py`
(`validate_structure`) plus `closure_hardened_0003.py` (`strict_structure`).
This adapter deliberately does not invoke their installation, discovery,
native-execution, current-host or protected-original-proof operations.
Original host SONAME resolution, actual bytes/modes, actual complete ELF graph,
wheel archive contents and installed runtime origins remain required checks for
the later fixed packaging/bootstrap consumers. A metadata result explicitly
sets `runtime_verified: false` and `member_bodies_read: 0`.

`body_json.parse_original` is separate from the signed-control i64 codec. It
retains original finite floating-point values and integer values without an i64
coercion, while refusing duplicate keys, unpaired Unicode surrogates, excessive
nesting and nonfinite values, including lexical overflow such as `1e309`.
Original bytes remain the identity input; this parser never creates a replacement
canonical source digest or normalizes combining Unicode characters.

This pure construction module does not itself consume a semantic graph or
satisfy T09's T08 acceptance dependency. The versioned consumer in
`COMPOSITE-CONTRACT.md` binds the complete independently reviewed T08 successor,
exact `/R02_environment` mapping, schema/module origins and selected execution
bytes. The low-level `original_value` return is internal comparison data; the
public composite result exposes aggregate counts and fixed obligations instead.
Final selected unit dispatch and independent whole-unit review remain required.
