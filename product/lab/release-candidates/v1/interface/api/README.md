# Authenticated candidate reader API

Two real handlers are available: `lab.status` and `catalog.get`. The adapter reads independently pinned saved candidate archives through verified signed replay. It runs over local stdio with a freshly provisioned reader policy and Ed25519 challenge authentication.

The six inspection CLI commands remain available in the adjacent `inspection` package. This API adds authenticated discovery and catalog pagination; the other 32 declared handlers remain unfinished.

## Inspect the observed result

- `examples/operator-journeys/api/0005/result.json` records eight actual child processes and their terminal outcomes.
- Each example directory contains exact client/server frames, frame hashes, its public reader policy and child stderr. LF framing is excluded from byte hashes.
- `receipts/attempts/0006/tests.stderr` records all 61 final guard checks.
- `receipts/R03-0003.json` binds this package, the examples, original schema inputs and preceding inspection/coupling evidence.

Paths above are relative to `product/lab/release-candidates/v1`, except the receipt paths which are relative to this directory.

## Run an isolated technical example

From the repository root:

```bash
python3 product/lab/release-candidates/v1/interface/api/exercise_stdio.py \
  product/lab/release-candidates/v1/examples/operator-journeys/api/NEW-UNUSED-DIRECTORY
```

Choose a new, unused directory under that example root. The runner owns new temporary reader credentials and read copies, runs the actual stdio server, retains public evidence and removes its temporary credentials. It creates no operational store or canonical admission.

An independently provisioned client starts `serve.py --policy /tmp/OWNED-DIRECTORY/reader-policy.json --policy-sha256 EXPECTED-SHA256`. It receives a challenge, signs its compact sorted UTF-8 encoding with the policy's reader key, sends the closed proof, then uses the returned context reference for calls. The host creates the trusted context. See `authentication.schema.json`, the original API call/reply schemas and `DESIGN.md` for exact contracts. Reader permission permits zero actions.

## Remaining work

Complete artifact inspection/query, the remaining exact API handlers, SQLite read parity, candidate queue/Decision coverage and Agent/session operational journeys. S02/R08 must review the complete exact candidate package. These technical examples establish no human pilot or owner admission outcome.
