# Decision carrier and exact-binding checker

`Exact proposal + selected option + attributable statement + scope -> inspectable decision record`

**Decision** means a recorded choice concerning an exact subject and scope. An authorized decision additionally needs a decision-maker with the right authority. This prototype checks the record's structure and internal agreement; it does not authenticate that authority.

**Why this matters:** an approval for one candidate must not silently become an approval for changed bytes, a different option, a broader scope or another effect.

## What works

The checker binds a decision to an exact proposal, subject file, declared subject-material manifest and structured statement. It verifies every declared material, option uniqueness, the selected option's effect, scope, proposal identity, actor/role assertions, timestamp and provenance. The statement must reference the same proposal digest.

```text
Same proposal, materials, statement, choice and scope -> record integrity verified
Changed candidate or implementation file -> rejected
Review option relabeled as permission to enforce -> rejected
Consistent actor assertions -> identity and authority still unverified
```

The example uses the preceding Constitution candidate and all 31 files in its frozen material manifest. Its actor, timestamp and choice are explicitly simulated. It does not record the user's approval of that Constitution or grant adoption.

## Try it

From the Lab root:

```bash
cd evidence/migrations/cyberalchemy-v2-to-lab/candidates/0008-decision-carrier
python3 check.py artifact-types/decision/v1/fixtures/valid/decision.json
```

Exit 0 means the record passes the integrity checks. Exit 1 means the input is invalid, a binding has changed or records disagree. The command is read-only.

The result explicitly reports `principal_authenticated: false`, `role_authority_verified: false`, `effect_authorized_by_checker: false` and `effect_executed: false`. These remain false even for internally consistent records labeled `recorded-owner-statement`.

The complete generated example is in [DECISION.md](artifact-types/decision/v1/fixtures/valid/DECISION.md). The input proposal and statement are under `examples/`.

## Verification

Run `PYTHONDONTWRITEBYTECODE=1 python3 validate.py` from this directory. It checks shared Artifact Type mechanics, 15 behavioral tests, eight invalid schema fixtures, deterministic regeneration and all 195 reconciliation entries. The demonstration verifies the preceding candidate's 31 declared files and preserves its bytes.

The semantic bindings reuse existing definitions rather than inventing a new normalized meaning: Authority Model, Exact Publication Authorization Invariant, Experiment Design, Experiment Run, Product Thesis and the currently admitted Goal version. Construction closes over 38 candidate Definition dependencies, with 30 dependency source sections checked, plus all five original Decision source selectors. Twenty-one inherited source-lineage residues and the earlier D53 narrow binding remain explicit.

[Validation evidence](receipts/validation.json) and [demonstration evidence](receipts/demonstration.json) describe the exact checks. Revalidation writes fresh candidate-local evidence; create a new review snapshot if an older `manifest.json` no longer matches.

## Migration state

| State | Before | After |
| --- | ---: | ---: |
| Current recorded admission | 13 | 13 |
| Constructed candidate | 81 | 82 |
| Scaffold awaiting implementation | 101 | 100 |

The next scaffold in ledger order is `type.schema`.

## What a later Product review would accept

`Recorded choice -> exact material and scope checks -> clear integrity result`

The reviewable capability is this exact Decision record type and integrity checker. Authentication, role-authority verification, effect execution, decision admission and verified supersession chains remain outside its scope.

File hashes detect changes to selected bytes; this read-only prototype does not make storage append-only, prevent filesystem edits, lock concurrent writers or establish completeness beyond the declared material manifest. The supersession policy requires new records, but storage enforcement is separate work.

## Open questions

- The authority owner owns principal authentication and verification of role scope.
- The decision owner owns append-only storage and verified supersession history.
- The source Definition owners retain inherited lineage residue and the D53 layout question.
