# Local chain fixture 0001 — runnable Docker profile

Status: **runnable local fixture; ready for independent review**. This is a new
profile alongside the existing `lab-fixture` service. The reviewed command is
`docker compose -f implementation/lab-runtime/local-host/compose.yaml run --rm chain-fixture`
from the repository root. The selected run on 20 October 2026 exited 0,
printed `PASS`, and left no matching Docker container. Its stdout, stderr and
receipt are retained in this directory. Normal and optimized unit suites pass
8/8 each.

The service executes the admitted v1 Work journey, then signs a fresh local
15-record/10-relation source with a disposable Ed25519 key. Reader verifies
the selected same-run public key, exact signed bytes, Work receipt digest,
scope and 20-minute period. Mapper projects 15 nodes and 10 closed edges.
Context checks the Source and mapping digests and returns 25 bound references.
The code tests body tampering, foreign key and Work digest, wrong scope,
expiry, duplicate source relation and mapping mutation. Temporary files are
removed before PASS; the Compose root is read-only, has no network or volume,
and publishes no port.

The signer is self-selected inside one run. This is a **fixture proxy** with
`original_roles_executed: false`; it does not execute the original protected
Source8, Reader, Mapper or Context role packages, issue a protected grant, or
qualify the original runtime plan. The checkout mount is read-only but
owner-readable protected files could be read by this UID; this fixture
intentionally selects only its named Work inputs and generated data. The
historical `/tmp` one-shot effects are not used as current inputs.

The smallest next original-role unit is to run the existing reviewed Source
builder on a fresh public cut in an owner-only durable root outside `/tmp`,
then cold-open its new signed package with a freshly rebound Reader selection.
That dynamic package digest must be carried through fresh Mapper and Context
selections; historical receipt hashes cannot substitute for live bytes.
