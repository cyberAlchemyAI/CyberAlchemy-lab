<!-- Generated from validation.json by tooling/validators/craft_transplant.py. Do not edit. -->

# Craft transplant validation

- Result: `PASS`
- Files verified: `2368`
- Bytes verified: `14865014`
- Source tree digest: `a501824e4b8b5bf3e3947b7e45db1040b598db572f97f8981b0143d0ec18f931`

## Checks

- `PASS` — source-selection-exact: manifest and Git selection contain 2368 ordered paths
- `PASS` — copied-bytes-exact: every source, manifest, and destination SHA-256 matches
- `PASS` — copied-modes-exact: every selected source and destination permission mode matches
- `PASS` — destination-closure: destination contains exactly 2368 selected files
- `PASS` — development-excluded: no development subtree was copied
- `PASS` — tree-digest-exact: ordered entry manifest reproduces the selected tree digest
- `PASS` — counts-exact: manifest counts equal reopened destination files
- `PASS` — source-remains-read-only: copy contract grants no source mutation
- `PASS` — prototype-not-overwritten: P0-P2 paths are outside the transplant destination
- `PASS` — authority-zero: copy and proposal claim no admission or activation
- `PASS` — human-projections-present: proposal, construction chain, and source epoch have colocated generated human views
- `PASS` — construction-chain-bound: successor chain binds the transplant architecture and validation receipt
- `PASS` — next-frontier-runnable: the next product-construction frontier is the read-only rebinding inventory

## Boundary

PASS proves only that the selected tracked DomainSpec v2 files were copied under craft/ with exact bytes, modes, inventory closure, and zero claimed authority. It does not prove active-name rebinding, runtime conformance, product approval, admission, release, or deployment.
