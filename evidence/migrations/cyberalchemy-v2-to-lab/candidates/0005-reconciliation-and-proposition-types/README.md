# Proposition reconstruction batch

`Source meanings -> three distinct record types -> working validation -> readable examples`

Lab can now check whether a proposition record supplies the information required for its declared role:

| Role | Plain-language definition | Required distinction |
| --- | --- | --- |
| Axiom | A starting proposition taken as given within a scope. | Names its domain, downstream dependents and the impact of revision. |
| Premise | A working assumption used to proceed while still unproven. | Records provisional reliance, conviction and revision/retirement conditions. |
| Hypothesis | An idea framed for testing. | Records a test and possible support/refutation; it is not automatically a working assumption. |

These roles are separate categories, not a promotion ladder. High conviction does not make a premise true. Passing validation means the record fits its contract; it does not establish the proposition as true.

## Try the capability

From the Lab root:

```bash
cd evidence/migrations/cyberalchemy-v2-to-lab/candidates/0005-reconciliation-and-proposition-types
python3 check.py artifact-types/premise/v1/fixtures/valid/proposition.json
```

The example provisionally assumes that the selected source files will remain unchanged during an import. It supplies a hash-check strategy and a rule for stopping if that assumption fails.

```text
Unproven assumption + high conviction + revision route -> PASS for a Premise record
Same record claiming proven truth -> BLOCK
Hypothesis marked as already relied upon -> BLOCK
```

Use `axiom` or `hypothesis` in the example path to inspect the other roles. Complete generated explanations are beside each example in `PROPOSITION.md`. `check.py` is read-only and returns a nonzero exit status for invalid or unknown records.

## Recovered migration state

The [reconciliation](RECONCILIATION.md) maps every one of the original 195 targets to current evidence, following the selected D65 successor mapping without erasing the older identities.

| State | Before this batch | After this batch |
| --- | ---: | ---: |
| Current recorded admission | 13 | 13 |
| Constructed candidate | 76 | 79 |
| Scaffold awaiting implementation | 106 | 103 |

A scaffold describes a proposed target. A constructed candidate has its machine contract and implementation material. Admission is a separately recorded decision; neither counts nor a successful check grant it.

## Why this batch comes first

The selected migration plan calls for shared mechanics and semantic-authority carriers first. These three missing carriers reuse existing Artifact Type mechanics and the already reconstructed meanings of Axiom, Premise and Hypothesis. Their construction dependency graph closes over 29 Definition candidates. Eight unmapped legacy references remain explicitly recorded as source-lineage residue.

The batch checks 26 source sections. A source layout change placed newer resilience definitions inside the old Axiom section boundary. [source-rebinding.json](source-rebinding.json) binds six unchanged meaning-bearing subsections exactly; the historical whole-section mismatch remains explicit. The source document and older candidates are preserved.

## Verification

Run from this directory:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 validate.py
```

Validation checks all 195 ledger entries, hash-bound admission evidence, transitive construction dependencies, source meaning, all three shared Artifact Type contracts, 21 invalid fixtures, deterministic regeneration and 10 behavioral tests. It updates only this candidate's generated material and validation receipts.

To regenerate the carrier packages explicitly, run `python3 author.py`, followed by `python3 reconcile.py` and the validator. Source rebinding is explicit evidence: it is not silently refreshed by authoring or validation.

## Decision meaning and remaining work

`Validated records -> review whether the distinctions meet the need -> later decide where consumers use them`

A future Product review would accept the exact capability to distinguish and structurally validate these three roles, with the limitations below. It would not prove a proposition or install these types as repository authority. The user's implementation approval authorized this construction batch; final Product approval is not inferred.

Instance reference strings are preserved but their targets are not resolved by this prototype. Natural-language truth, test adequacy, domain-specific reasoning and promotion decisions remain outside its checks. The 103 remaining scaffolds still require their own implementation batches; this is not completion of the whole migration.

## Open questions

- The source Definition owner owns repair of the D53 section layout and its later question/consumer boundaries.
- The Artifact Type owner owns any later admission and instance-reference resolution contract.
- The reconstruction ledger owns selection of the next missing carrier batch.
