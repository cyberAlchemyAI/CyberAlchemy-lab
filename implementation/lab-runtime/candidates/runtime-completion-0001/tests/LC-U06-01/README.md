# LC-U06-01 provisional fixture construction

Run from the repository root:

```bash
python3 -B implementation/lab-runtime/candidates/runtime-completion-0001/tests/LC-U06-01/test_fixture_provisioner.py
```

The suite creates two separately selected disposable stores through the original
pinned C11 v2 engine and uncached replay bridge. It exercises fresh per-run
reader keys and challenge nonces, selected `/tmp` policy staging, prior-policy
detachment and retained bytes on restart, pre/post directory and file custody,
source-drift and alias refusal, durable no-replace intent/result records, and
read-only effect inspection after a simulated lost response. Fixture roots are
created under `/tmp` and removed by their owning test process; no key or raw
private input is written to the repository.

The original T34 provisioner is broader: it requires an independently selected
operator, permanent owned store and key custody, genuine protected channel
inputs, actual host/source/profile authority and two authorized rehearsals.
This code is visibly fixture-only and offers no actual-authority entrypoint.
LC-U05-03 has not passed its whole-unit original protected-startup oracle, so
LC-U06-01 cannot be selected or accepted by the plan runner from this work.
The eventual exact operational adapter and original ReaderChannel validation
must be reviewed against current selected inputs before unit acceptance.
