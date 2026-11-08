# T25 original package accounting

`account.py` cold-reads the pinned final-review inventory and final-member input selection. It accounts for all 363 distinct original members, including the historical `member_id` and `member_ref` row forms, and rehashes all 681 selected public files. `RESULT.json` is deterministic and records the 363 member references without body export. Four normal and optimized tests pass for the exact inventory, duplicate member, changed selected file and changed inventory selector.

Run `python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t25-original-package-accounting-0001 -p 'test_account.py' -q` from the repository root and repeat with `python3 -O -B`.

This is an accounting foundation. It does not include the new local additions, build a final package, replay an installation, grant protected content access or satisfy T25. Those effects require the final selected T15 cut and remaining runtime tests.

`bundle.py` now builds a deterministic, disposable ZIP from the same pinned
selection, with the two original control files, an explicit manifest and all
681 exact public file bodies. `replay()` checks the controls, manifest, paths,
mode, uniqueness, canonical archive bytes and each body hash, then reconstructs every selected file in
an empty temporary root and reads it back. The [replay receipt](BUNDLE-REPLAY.json)
records the stable archive SHA-256 and 363/681 accounting; no archive or
protected body is retained. Eight bundle tests pass normally and under `-O`,
including changed control/body, missing/escaped member, duplicate JSON key,
ZIP comment and trailing-residue refusals. Run `python3 -B bundle.py` from this directory to reproduce the
receipt.

This is only the **original public input package**. New local additions,
member-specific dispositions, final selected runtime bytes, installed-product
replay and the T25 final package remain open.
