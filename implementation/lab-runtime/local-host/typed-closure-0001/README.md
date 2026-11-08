# Typed mixed-closure verifier — T08 engineering slice

`closure.py` verifies every selected byte by SHA-256, including a 27 MiB proof input, but traverses only explicit `semantic-artifact` dependency edges. `provenance-evidence`, `public-package`, and `protected-host` bindings are verified separately. Protected host input must be an owner-only regular file outside the repository, read without following symlinks; the result includes counts, never the protected content.

Five focused tests exercise mixed graph/proof inputs, large proof reading, a semantic cycle, changed proof bytes, an illegal proof edge, a protected symlink and loose protected mode. They also reject a FIFO without blocking and a protected path replaced during reading. This is the first typed-reader/graph-selector slice. It is **not yet** wired to the selected API release schema or its original proof table, and it does not close T08's complete 27 MiB original closure. Its manifest dependency edges are caller-declared until that integration binds them to the schema.

```bash
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/typed-closure-0001 -p 'test_*.py' -q
```
