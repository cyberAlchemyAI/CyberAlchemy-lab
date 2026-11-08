# Disposable local four-phase chain fixture

Run from the repository root:

```bash
docker compose -f implementation/lab-runtime/local-host/compose.yaml build chain-fixture
docker compose -f implementation/lab-runtime/local-host/compose.yaml run --rm chain-fixture
```

The command executes the admitted v1 local Work journey first, including an
approved local transaction, changed-proposal refusal, exact retry and
fresh-process replay. It then creates a new, self-signed, 20-minute fixture
Source with 15 records and 10 relations. The Reader phase verifies the
signature against the same-run selected public key, the Work receipt digest,
scope and period. Mapper projects 15 nodes and 10 edges and checks endpoint
closure. Context binds all 25 mapped references to the exact Source and mapping
digests. The container removes its temporary files and prints a PASS only after
all four phases complete. A failed phase exits nonzero.

This is a **fixture proxy**, not execution of the original protected Source8,
Reader, Mapper or Context role packages. The generated key is not an
independently enrolled signer, and no protected grant or historical plan gate
is satisfied. The Compose mount is read-only and runs as the checkout owner;
that account can still read owner-readable repository files. The fixture code
intentionally selects only the admitted Work runtime and its own generated
records; the mount is not a protected-data isolation boundary. Docker uses no
network, a read-only root filesystem, dropped capabilities, no-new-privileges
and temporary in-container state. It publishes no port and retains no fixture
volume.

The next original-role integration unit is a fresh Source build from the
reviewed public cut into an owner-only durable location outside `/tmp`, followed
by a signed Reader cold-open on that exact package. Its new dynamic Source
digest must be bound into fresh Mapper and Context selections. The historical
one-shot `/tmp` attempts cannot be replayed or treated as current input.
