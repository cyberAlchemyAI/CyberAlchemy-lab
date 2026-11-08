# T16 selected 4.23 successor proof

This is a local engineering candidate, with no protected Source8 or authority
effect. It does not assert complete inherited-method qualification.

The selected install is the existing owner-only `/tmp/cal-T03-native-install-20261023/0001`
(Python 3.14.4, jsonschema 4.23.0, cryptography 46.0.5). The native reader's
SHA-256 is `fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c`,
the same digest pinned by the historical mapper. The historical `/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader`
locator is absent. The byte-equivalence evidence is `NATIVE-REBIND-PROOF-0001.json`.

The new local source family is `instances/legacy-local-e084574c6d149cf0`.
Its Source, independent cold replay, Reader, Mapper, and Context phases passed
with separate receipts. Private signed source material stays in the owner-only
local share outside Git. API60 pins this family and passed one inherited
current-family method, but its historical custody route still selected the
expired original 0148 source and missing native locator. `one-historical.log`
preserves its exact 0-run setup refusal. A broad API60 attempt was stopped
after the same failure; `working/api60-first-20261023/PARTIAL-LEDGER.json`
accounts for all 345 selected IDs without treating unexecuted methods as passes.

API61 is a disjoint successor at
`product/lab/release-candidates/v1/interface/api-integration-v61-t16-abi423-bridge-0001`.
It selects the fresh signed family for the inherited `custody-participation`
bridge and recuts the fresh period expectations. Its inherited test files are
byte-identical to API60. Across the API53 inherited inventory, all 345
`test_*` method ASTs are unchanged. Two whole test files differ from API53
because three hard-coded family-ID literals in class setup/helpers were
retargeted to the fresh signed family; see `METHOD-AST-COMPARISON-0001.json`.
Source SHA-256:
`84435a57c990a1d85504cf844a257e6dc3607c81519d368c828449ac8106ffc4`;
profile SHA-256:
`843ee830613211f6c36c6c822ef32b08e71b5799166485ed24b99d09f053e12c`.
The actual selected-ABI two-method run in `api61-two-methods-rerun.log`
passed unchanged `MetadataScopes.test_00_current_metadata_after_original_Assignment_expiry`
and `CurrentControls.test_02_new_source_keeps_original_expired_period_exact`
in one process (2/2, 0 errors, 0 failures). This establishes one historical
adapter and one current-family method on the same cut, not all inherited
method semantics.

The bounded API61 parallel attempt was interrupted after `installation.execute`
reported `integrity-failed`. Direct preparation traced that refusal to two
`guarded_candidate.py` custody scopes: the selected fresh Context producer was
paired with the old `custody_context_sessions.DELIVERY_PIN`. The immutable API61
source/profile and `working/api61-full-20261023/INTERRUPTED-LEDGER.json` retain
that failure and exact unexecuted accounting. Parallel execution is unsafe for
the inherited installation tests that deliberately alter selected API bytes.

API62 recut both custody guard scopes to the fresh Context producer. Its
source/profile SHA-256 values are
`9c39d58572139a731d610bb0cf174655892106b805985567762c2041a98b94be`
and `c98076fd86b3fced1d7b356017efd234c0205b62c7f357a28419d709d56e5258`.
The actual inherited installation positive and real preimage-change negative
passed 2/2 in `api62-install-focus.log`. The old/wrong-family pin and an
isolated byte-changed copy of the fresh Context manifest both refused in
`api62-context-refusals.log`; the selected family was not modified. One
inherited current Session memory-erasure method passed in
`api62-session-focus.log`. API62 `OriginalAPI.test_01` still failed before
assertion because the public `legacy_delivery()` alias selected the expired
Source5 producer and its deleted executable locator. Its exact traceback is
in `api62-custody-focus-rerun.log`.

API63 is the fresh-family alias successor at
`product/lab/release-candidates/v1/interface/api-integration-v63-t16-abi423-alias-0001`.
Its source/profile SHA-256 values are
`fc079aaf4390c8d523cb4036ef31421d146a663cc135694f492e02387b879edf`
and `022ede7e9c70975bc2aa33d9f99f81b3f16eb7145e6c341734fa3bd5681b2662`.
The public historical-adapter alias now selects the signed current family;
the expired producer remains separately named and pinned for truly historical
selection. Custody Session source markers, policy period and Machine scope
select the same current family. The inherited OriginalAPI reader/profile
methods passed 2/2 in `api63-custody-focus.log`. An actual authenticated
`custody-participation` Service selected the fresh Session runtime and returned
`lab.status` in `api63-custody-alias-session.log`. All 345 inherited `test_*`
method ASTs still match API53, with the same two disclosed setup/helper
retargeted files; see `METHOD-AST-COMPARISON-API63-0001.json`.

The final API63 focused retests passed: two actual inherited installation
methods (positive byte-closure and real preimage-change refusal) in
`api63-install-focus.log`, and one inherited current Session memory-erasure
method in `api63-session-focus.log`. `run_regression_api63.py` enforces one
fresh selected-ABI worker at a time, captures per-class terminal outcomes,
and accounts for all 345 IDs. It stops after a failed class and marks
remaining methods unexecuted. The run `api63-serial-20261023` is active in
`working/api63-serial-20261023/`; a complete inherited regression PASS is not
yet established.
