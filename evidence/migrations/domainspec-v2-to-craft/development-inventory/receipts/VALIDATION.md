# Development inventory validation

> Generated from `validation.json`. The JSON is canonical; this file is a human projection.

Overall result: **PASS**

- **PASS** `INV-01-DIRECTORY-COVERAGE` — 58 directories represented exactly once
- **PASS** `INV-02-TRACKED-COUNT` — 9190 tracked development files
- **PASS** `INV-03-UNTRACKED-COUNT` — 3908 untracked nonignored development files
- **PASS** `INV-04-LEDGER-COVERAGE` — 126 ledger development artifact records classified
- **PASS** `INV-05-BASELINE-DENOMINATOR` — canonical baseline denominator is 771
- **PASS** `INV-06-BASELINE-RECONCILIATION` — 742 exact baseline bytes, 24 source-drifted members, and 5 missing paths reconcile to 771
- **PASS** `INV-06A-NO-CRAFT-ONLY-BASELINE-DRIFT` — every present baseline member in Craft exactly matches the current source byte
- **PASS** `INV-07-SOURCE-UNCHANGED` — tracked, source-like untracked, and status epochs unchanged during generation
- **PASS** `INV-08-CRAFT-UNCHANGED` — Craft tree digest unchanged; no development file was copied
- **PASS** `INV-09-MACHINE-PARSEABLE` — canonical inventory parses as JSON
- **PASS** `INV-10-PROJECTION-DETERMINISTIC` — human projection is deterministic from canonical JSON
- **PASS** `INV-11-ACTIVE-WRITER-HOLD` — current EVF and reference-consumer bytes are held from migration
- **PASS** `INV-12-NONAUTHORITY` — inventory grants no migration or lifecycle authority

## External check

- **not_evaluable** `BASELINE-V2-RUNTIME-VALIDATOR` — `node` is not available on the current shell PATH; no runtime validator claim is made.

## Claim ceiling

PASS establishes deterministic inventory coverage and no-effect generation only. It does not authorize or perform migration, acceptance, admission, publication, release, deployment, or retirement.
