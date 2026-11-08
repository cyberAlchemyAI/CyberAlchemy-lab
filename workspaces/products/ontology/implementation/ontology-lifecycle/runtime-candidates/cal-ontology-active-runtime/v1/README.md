# Local active ontology runtime candidate

This L5 candidate joins the admitted L4 state-bearing sandbox adapter to the
deterministic Rust event runtime. It calculates the 47-subject CyberAlchemy
ontology from the exact W7 event cut and keeps the result available while a
local process is active.

Run it from this directory:

```bash
CARGO_TARGET_DIR=/tmp/cal-ontology-active-runtime-target \
  cargo run --locked --bin cal-ontology-active-runtime
```

The process prints a JSON `ready` record. Enter one command per line:

- `status` — show the active local session and exact event cut;
- `projection` — show the event-calculated ontology;
- `help` — list commands;
- `stop` — restore the preimage and remove the sandbox.

stdin EOF also stops and cleans the runtime. The command accepts no path,
network, credential, live-mode, migration, or cutover arguments.

Validate and freeze evidence:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 validate.py --write-receipt
```

This is an unapproved, process-local product candidate. `prototype_runtime_active`
means the test process and its isolated projection are active. It does not mean
that a governed or live runtime has been activated.

The validator binds every selected event file through deterministic semantic
and governance directory digests, as well as the calculated projection digest.
