# Invariant carrier and observation checker

`A condition that must hold + scoped observation -> satisfied / violated / not evaluable`

**Invariant** means a condition on a system or its artifacts that must remain true within a declared scope. A violation means drift or a defect. This prototype records that condition and checks it against supplied data.

**Why this matters:** an imported rule becomes usable only when Lab can distinguish a detected violation from missing evidence. Missing observations must never look like success.

## What works

The first profile compares named integer observations using `equals`, `at-least` and `at-most`. Each invariant declares its subject, scope, required checks, grounding references and what a violation means. All comparisons are local and read-only; no arbitrary expressions execute.

```text
Expected nodes = 815 + observed nodes = 815 -> satisfied
Expected nodes = 815 + observed nodes = 814 -> violated
Expected documents = 422 + no document observation -> not evaluable
```

The current imported store was observed through the Rust runtime. It satisfied the example's three count checks: 815 nodes, 1,210 relations and 422 supporting documents. The runtime store's file hashes were unchanged before and after observation. [Live observation evidence](receipts/live-observation.json) records the exact rule, execution receipt and runtime head.

Matching counts establishes only those count checks. It does not prove record contents, continuous correctness or the authenticity and freshness of arbitrary supplied observations.

## Try it

From the Lab root:

```bash
cd evidence/migrations/cyberalchemy-v2-to-lab/candidates/0006-invariant-carrier
python3 check.py artifact-types/invariant/v1/fixtures/valid/invariant.json examples/satisfied.json
python3 check.py artifact-types/invariant/v1/fixtures/valid/invariant.json examples/violated.json
python3 check.py artifact-types/invariant/v1/fixtures/valid/invariant.json examples/missing.json
```

Exit codes are 0 for satisfied, 1 for violated, and 2 for not evaluable or invalid input. The output distinguishes invalid input from missing observations. Without an observation argument, the command validates the rule's record only and reports `not-evaluated`.

A known violation remains visible even if another observation is missing: the aggregate is `violated` with `observation_complete: false`. Every declared check retains its own outcome.

## Verification and migration state

Run `PYTHONDONTWRITEBYTECODE=1 python3 validate.py` from this directory to check the candidate and update its receipts. The live demonstration requires the existing imported store and its recorded runtime binary. Revalidation creates fresh evidence; regenerate an exact review snapshot before relying on an older `manifest.json`.

Verification covers 13 behavioral tests, eight invalid record fixtures, the shared Artifact Type contract, deterministic reconstruction, all 195 ledger entries and the real local import observation. Construction depends on 27 existing Definition candidates and 25 source sections. The previous D53 narrow source binding and eight source-lineage residues are retained explicitly.

| State | Before | After |
| --- | ---: | ---: |
| Current recorded admission | 13 | 13 |
| Constructed candidate | 79 | 80 |
| Scaffold awaiting implementation | 103 | 102 |

The next scaffold in ledger order is `type.constitution`. This batch preserves the previous candidate and admission records.

## What a later Product review would accept

`A declared invariant -> bounded comparison against an observation -> an explicit finding`

The reviewable capability is this exact record type and integer observation checker, including its missing-evidence behavior. It grants no type admission or automatic enforcement. General domain predicates, grounding-reference resolution, observation trust/freshness and proof across all states or time remain outside the profile.

## Open questions

- The Artifact Type owner owns additional predicate profiles and any later admission.
- The observation owner owns authentication, freshness and sampling coverage.
- The source Definition owner retains the D53 section-layout issue recorded by the preceding batch.
