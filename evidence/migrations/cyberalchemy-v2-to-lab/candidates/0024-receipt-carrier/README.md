# Receipt carrier

Exact local checker + exact input -> captured stdout, stderr and exit code -> repeat and compare.

A Receipt records what one bounded operation did and its exact inputs and outputs. This candidate binds Traceability semantics and preserves the normalized D36, D57 and D66 source selectors without treating publication or Context effects as implemented.

The example is produced by actually invoking the preceding Evidence Set checker on its frozen positive input. Its standard output and standard error are stored as exact files. The record binds the checker, predecessor snapshot, input, captured streams, exit code and Python version.

Verification first checks the frozen predecessor materials and accepts only that fixed checker and its fixed input. It then repeats the local operation with a 30-second timeout and compares both output streams byte-for-byte and the exit code. Changed digests, substituted implementations or inputs, forged outputs and inconsistent result labels are rejected.

A matching replay establishes current agreement for this bounded operation. It does not authenticate a historical actor, prove external execution or publication, or establish the truth of the evidence being inspected. The Python version is recorded, but this is not a complete operating-system or dependency lock. There are no timestamps or signed execution attestations in this profile.

The checker performs only the fixed local replay. It does not execute an arbitrary command supplied by a receipt, mutate source data or authorize downstream actions. The prior candidate snapshot remains unchanged.

Run from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0024-receipt-carrier/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0024-receipt-carrier/check.py evidence/migrations/cyberalchemy-v2-to-lab/candidates/0024-receipt-carrier/artifact-types/receipt/v1/fixtures/valid/receipt-record.json
```

CLI status 0 means receipt replay agreement; 2 means invalid input or disagreement. Status 0 grants no authority.

Validation passes 14 behavioral tests and 8 invalid contract fixtures. It verifies the Traceability Definition and its source section, all three normalized D36/D57/D66 selectors, and the existing D53 overlay. The selected Definition closure has no source-lineage residues; prior snapshots preserve inherited residues. Reconstruction repeats the bounded operation and reproduces its captured output and generated records.

The 195-target ledger now has 13 admitted targets, 98 constructed candidates and 84 remaining scaffolds. Next: `type.projection-spec`.

The user's `next` authorizes construction, local execution and testing. A later reliance decision would approve treating this exact receipt as evidence of its bounded operation. It would not approve a publication, external effect or governing conclusion.
