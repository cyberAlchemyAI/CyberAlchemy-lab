# T06 current composite successor: independent cold review

Review scope: `t06-current-composite-successor-0001`, the current API33 composite SDK `revision-0001`, its branch fixture producer/driver, and the staged task-local public dependency installation. No Docker or private branch construction was run in this review. The selected API33 source manifest was SHA-256 `704c6fddbadc56a7bb3c2af12723d31f613de2618119d6d933edf2ec8fd56f02` at readback; the SDK source manifest was `85dcd0463465d3e8e767448c73e414a7debd875606f2519c949d9f74549874b6`.

## Verdict

The public installation and executable source closure passed cold verification. Actual three-branch startup and the 34-operation catalog remain unobserved. The current API33 contract profile does not yet select the new SDK manifest or branch preparer/driver, so the SDK's own `software_guard` correctly refuses live startup until a new exact API33 profile/source successor is selected.

## Finding T06-R1: installation provenance is not runtime-pinned

`control.installed()` verifies SHA-256, size, mode, owner, no-follow attachment and a closed inventory for all 1,010 selected dependency files. It permits `installation.json` as the sole extra file but never verifies that file's SHA-256, size, mode or owner. `stage_installation.py` copied the historical file and recorded SHA-256 `5821d37ce536e08c639493ceb8d165949e65cf5dd9771af5576a724082cca13b` in `INSTALLATION-0001.json`, but the live launcher does not consume that digest. In a disposable one-file analogue, changing the metadata bytes and mode to `0777` still passed `installed()`, while changing the selected file was refused. This does not undermine the selected executable bytes; it means the historical installation provenance cannot be claimed as live-pinned. Repair by selecting the metadata digest, size, owner and mode in the installed guard, with a metadata mutation negative, or narrow the receipt/README wording to say provenance was checked only at staging.

## Finding T06-R2: dual integration-member origin

Current API33 `contract-profile.json` still binds `integration_members_binding.path` to `api-integration-v16/integration-members.json`. API33 also contains a byte-identical local copy (SHA-256 `64931c417e6738d82c1c4cb819bb660237aab038bf6474594d421d8991f6d7d1`), and T06 `software_guard()` reads that copy while checking only that its digest equals the profile binding digest. The SDK test deliberately accepts a v16 profile path. API33's `integration_dispatch` follows the profile path, so the runtime has two selected origins for the same member bytes. The API33 producer confirmed this is inherited from v30 and recommends a sixth successor profile/source re-pin to the API33 local path and exact profile file row. Until then, the T06 claim should state this dual-origin condition rather than call the member origin wholly current. The exact bytes do match; this is a lineage issue, not a demonstrated functional mismatch.

## Evidence and limits

- Re-ran six focused tests: 6/6 pass. They cover SDK and branch source manifests, inherited three-branch shape, API33 origin refusal, public installation closure, and missing-row/source-profile negatives. They mock child startup; they do not prove a live branch.
- Re-ran the SDK `installed()` guard against the staged installation: 1,010 selected files verified, no generated `.pyc`. All 16 path/digest references in `working/RUN-0003.json` matched current bytes.
- Static inspection found actual Base, Action and Governance channel/service constructors and reverse owned cleanup in `composite.run()`. The driver sends independently signed branch proofs, observes common `Base28+Action3+Governance3` readiness, and closes stdin for an owned exit. This is a code-path observation, not execution evidence.
- Current API33 profile contained none of the new SDK manifest, branch preparer or branch driver rows at this review. Fresh exact API33 re-pin and actual child challenge/readiness/clean exit evidence are required for a live T06 claim. Even a startup pass will execute zero dispatch operations and will not qualify the full API class or admit a governance outcome.

## Cold re-review of the revised SDK

The T06 producer revised the SDK source manifest to SHA-256 `277209c322c7891fb8c99533ed8280b1343c8f7bbb0ec68f090abbcd0d1b7b4a`. `control.installed()` now pins the historical metadata digest, 509,519-byte size, owner and mode both before and after inventory. The stage script checks the source metadata against the same exact binding. Independent disposable mutation checks accepted the original and refused changed bytes and mode; 7/7 normal and 7/7 optimized focused tests pass. **T06-R1 is resolved for the revised SDK.**

The revised `software_guard()` requires the integration-member binding to name the exact current API33 file and digest, and its focused test refuses the v16 alias. **The T06 side of T06-R2 is resolved**, while current API33 profile/source still have the inherited v16 binding and do not yet select the revised T06 rows. A new API33 successor re-pin and live branch run remain necessary. The earlier `RUN-0003.json` pins the previous SDK and is historical evidence; it must not be reused as a receipt for these revised bytes.

The producer's fresh static receipt `working/RUN-0004.json` is SHA-256 `2859b05a2ff9102e84427cf4da867e4c02b648c4523f20b10f881f385e2211c6`. I independently rehashed all 17 file/size bindings it names; none drifted. Its selected launcher negative returned 2 with `startup-or-channel-refused` for an intentionally absent config and binds the revised SDK manifest; it proves bootstrap reachability, not a branch startup. The receipt accurately reports `actual_branch_startup=false` and `actual_full34_qualification=false`.
