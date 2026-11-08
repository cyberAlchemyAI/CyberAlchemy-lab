# Selected native child launcher

The static C launcher preserves the selected private ABI for existing child and
grandchild calls through `sys.executable`. It derives the repository from its own
actual executable path and selects the adjacent `.cal-runtime/native` directory.
It verifies all 1,010 original native files and their closed inventory, modes,
sizes and SHA-256 hashes before executing the selected loader and real Python.
It also verifies the exact selected child bootstrap before execution. No host
Python, shell, dynamic loader interpreter or libcrypto supplies that check.

`build.py` selects the independently pinned original public installation receipt
and emits a deterministic member table and static binary. Two builds from
different temporary build directories must have identical bytes. The runtime
requires isolation, no bytecode and no site initialization. Supported leading
interpreter flags are explicitly parsed; unknown settings refuse with exit126.
Potential loader and Python injection environment variables are removed before
the selected interpreter is started.

The real bootstrap is owned by `t25-integrated-runtime-0004`. It verifies the
fresh installation receipt and selected public closure, sets `sys.executable` to
the attested launcher for future children, and preserves the real interpreter
identity separately. A launcher hash must never be reported as a Python ELF hash.

Component tests use an explicitly named small fixture bootstrap and actual
selected native bytes. They prove private ELF maps and dependencies in parent,
child and grandchild, refusal of native/body/bootstrap/flag substitutions, static
ELF posture, and reproducible builds. This is separate from the final bootstrap,
source guard, API or whole-package qualification.

The operator owns the private installation and selected public package. These
checks assume no concurrent hostile writer with that same host authority during
verification and execution; they do not claim protection against that host
administrator or an arbitrary same-UID replacement race. The fresh installation
receipt's semantic/inode binding remains the real bootstrap provider's job.

The current reviewed checkpoint is `ACCEPTANCE-0002.json`, with bootstrap
`8a7f8361...` and launcher `fe36a908...`. Ordinary test discovery now runs exactly
seven tests; fixture setup is reused without inheriting another lane's tests.
Both normal and optimized discovery passed. Ordinary tests never replace retained
evidence. Explicit collection uses a new path and refuses an existing file:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover \
  -s implementation/lab-runtime/local-host/t25-native-launcher-0001 -p 'test_*.py' -q
PYTHONDONTWRITEBYTECODE=1 python3 -B -O -m unittest discover \
  -s implementation/lab-runtime/local-host/t25-native-launcher-0001 -p 'test_*.py' -q
# Optional: choose a new proof filename; this command never overwrites it.
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  implementation/lab-runtime/local-host/t25-native-launcher-0001/test_real_bootstrap.py \
  --evidence-output /tmp/new-launcher-process-proof.json -q
```

The pre-repair discovery ran thirteen extra inherited cases with the wrong
fixture phase and failed. It also replaced the original randomized retained
proof. That failed review log and superseded acceptance remain historical;
`0002` binds a fresh explicitly collected proof and the repaired test harness.
No source, API, permanent package or T19/T25 completion follows from this component.
