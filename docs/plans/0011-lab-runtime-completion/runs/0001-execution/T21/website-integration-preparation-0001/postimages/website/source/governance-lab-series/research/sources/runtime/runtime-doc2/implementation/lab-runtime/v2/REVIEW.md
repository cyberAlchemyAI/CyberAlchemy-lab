# Review: D75 source-profile successor

Status: candidate. One owner decision may admit this exact successor package after reviewing its bytes and appropriate evidence. D75 admitted v1; it supplies no implicit admission for v2.

## Purpose and order

1. Keep the exact D75-admitted v1 package unchanged.
2. Build a successor profile over the four immutable foundation roots plus the D75 operational admission root.
3. Select D75 State and histories and retain exact historical endpoints; verify the 17 new records against their admitted schemas in the successor suite.
4. Adapt the original 33 tests and add five D75-specific checks; run the complete suite in isolated worker processes and run the demonstration.
5. Bind the exact candidate package to outcomes; present this review and example before admission.

## Revised behavior

| Surface | Admitted v1 | Candidate v2 |
| --- | --- | --- |
| Selected repository State | D74 | D75 |
| Selected history cursors | 4 / 4 | 5 / 5 |
| Vocabulary registries | D74 | D74, unchanged |
| Runtime v1 Implementation record | Outside selected admissions | D75-admitted artifact revision |
| D75 deterministic relations | Outside selected admissions | Six exact recorded connections |
| Current-State lookup | Unconsumed | Checked against immutable D75 selection; no replay authority |
| Default local store | `.local/lab-runtime/store` | `.local/lab-runtime/v2/store` |
| Older-profile store | Frozen to its baseline | Readable as stale; new writes/context blocked |
| Protocol schemas | Six v1 interfaces | Same six interfaces, byte-exact |
| Implementation admission | Admitted by D75 | Candidate |

The validation runner also supports independent worker processes with per-check outcomes and complete-suite coverage. The runtime code changes are source overlay/selection checks, exact version selection for an implementation-symbol bridge, dynamic query scope, store/profile compatibility checks, and the separate CLI default store. Transaction generation, signatures, canonical schema interfaces, session memory and recovery code are inherited. Their successor integration is evaluated by this package's own validation receipt.

## Example before decision

Run:

```bash
python3 implementation/lab-runtime/v2/lab.py inspect implementation:cyberalchemy-lab:operational-runtime:v1 --record
```

Expected source-backed interpretation:

- Identity: `implementation:cyberalchemy-lab:operational-runtime:v1`.
- Exact artifact revision: `implementation:cyberalchemy-lab:operational-runtime:v1@decision-0075`.
- Effective instance admission: `admitted-current`.
- Source body's domain lifecycle remains `candidate`; this separate field is not rewritten by admission.
- Runtime activation remains `not-observed`.
- This v2 executable remains a candidate.

The package release label `implementation:cyberalchemy-lab:operational-runtime:v1@v1` is not an alias for the admitted artifact revision.

For a future bounded Work proposal in a provisioned v2 local branch:

```text
D75 State; semantic cursor 5; governance cursor 5
  -> prepare exact planned Work proposal
  -> review targets and deterministic consequences
  -> one exact operator signature
  -> one atomic local admission transaction
  -> local successor State; semantic cursor 6; governance cursor 6
  -> prepare ephemeral Agent context from that committed local HEAD
```

The validation demonstration exercises this flow in a disposable local branch; its exact outcomes are recorded in the validation receipt. Repository D75 remains unchanged. A multi-target proposal can share one approval; deterministic bookkeeping needs no second decision.

## Evidence and admission boundary

[Validation receipt](receipts/validation.json) binds all candidate files, each of the 38 test outcomes, and the actual isolated Work/context demonstration. Inspect the receipt's result before making any passing claim. [Source inspection receipt](receipts/source-inspection.json) separately binds actual repository read results and package hashes. Neither receipt admits this executable.

The five successor checks cover D75 schemas/edges, historical predecessors and package/artifact version separation, readable but blocked v1 stores, initialization with an exact active profile, and lookup binding/drift. The inherited checks cover all five target categories, revision/withdrawal, closed relation extension, exact signatures/approvals, replay/recovery, source drift, writer exclusion and ephemeral sessions.

One admission may cover this exact successor implementation and its reviewed evidence. The deterministic bookkeeping follows from that admission. Provisioning a permanent local operator/store or activating a service is a separate operational scope.

No new semantic Definition, Artifact Type, Relation Kind or repository admission is created here. Existing D73 unresolved version references remain visible diagnostics. The claim ceiling remains local process interruption and the selected source envelope, with no complete ontology coverage or production durability claim.
