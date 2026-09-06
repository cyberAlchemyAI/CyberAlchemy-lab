# Experiment profile

- `PROFILE_ID`: `cal-ontology-graph-read-model-benchmark/v1`
- `LIFECYCLE_OWNER`: CyberAlchemy ontology-product prototype construction
- `ARTIFACT_TYPE`: implementation benchmark
- `CONTRACT_PATH`: `../contract.json`
- `PROMPT_SET`: deterministic generated ontology graph workload
- `REGIME_SET`: `smoke`, `medium`, `large`
- `PROFILE_VALIDATION`: performed by `run.py validate`

## Quality bar

- Every generated subject has one exact projected challenge contract.
- The fixture and query traces are deterministic for one profile and seed.
- The scan control and actual read model return identical normalized results.
- Every mixed calculated delta is exactly equal to a full target rebuild.
- The delta receipt proves bounded rollback journaling and rejects a full-model
  clone as the transaction strategy.
- Concurrent readers observe only complete versioned `Arc` generations; an old
  snapshot remains readable after generation one is published.
- The publication receipt rejects a full-model staging clone and proves that
  unchanged subjects, challenge contracts, and index buckets are pointer-shared.
- Cold recovery must rebuild the exact model within the selected profile's
  explicit objective, bind the complete expected source envelope and index
  digest, and use no checkpoint.
- Governance-only changes cannot mutate semantic state without a new event.
- Two attempts produce the same fixture, result, index, target projection, and
  delta digests.
- Raw run logs and structured attempt evidence are preserved.
- Performance is reported descriptively; timing instability is flagged and
  never converted into a correctness failure or production claim.

## Anti-patterns

- Do not call generated fixtures canonical ontology events.
- Do not use one timing attempt as stability evidence.
- Do not omit slow or failed query families.
- Do not treat payload estimates as RSS.
- Do not infer concurrency, durability, crash recovery, production suitability,
  approval, admission, or activation.
