# T32 captured-code ontology recovery successor

This version repeats the API43-selected 25-semantic/25-governance ontology
package interruption run. Its child receives the profile-checked
`fixtures.py`, `recoverable_store.py` and `child_run.py` bytes over a private
pipe and executes them from memory. The fresh recovery child receives the
prehashed parent runner bytes the same way. The original ontology
`request.json` is selected and its 25/25 read cursors and digest are retained;
that file is a context-read selector, while the native batch-append request is
constructed from the package's exact selected event bodies.

The runner still verifies the old committed HEAD before recovery, recovers in a
new process, checks exact event arrays and the expected ontology cut, retries
without another effect, and preserves a foreign sibling. It records the
runner, child, captured executor, selected read request and package hashes.

From the repository root, run with the selected jsonschema overlay:

```sh
PYTHONPATH=implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/overlay \
  python3 -B implementation/lab-runtime/local-host/t32-api43-ontology-package-0002/run.py
```

The exact receipt is created once at `RUN-0002.json`. This remains a local
native technical route. API43 `ontology.project` does not call it, the top-level
Python runner and overlay are still host files, and process-kill evidence does
not establish power-loss durability or authority effects.

`test_captured_exec.py` runs two focused normal and optimized checks: a
substituted entrypoint path and a substituted imported-module path cannot
replace the captured bytes supplied to the child.
