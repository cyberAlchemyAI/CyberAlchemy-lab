# Exact local dependency staging

`preflight.py` verifies the independently selected R02 interpreter, eight wheels,
three host ABI files and native executable. It keeps all original bindings.
`install.py` stages public interpreter/native/wheel bytes into an exclusively new
child of an independently identified, mode0700 owned parent. It never adopts,
overwrites, deletes or recovers an existing generation. Failures retain their
partial owned output for separately selected inspection.

The copied native executable remains mode0755; extracted package files are
mode0644. A fresh isolated interpreter checks Python, SQLite and all package
versions. A no-argument native process proves the selected ABI entrypoint rejects
missing replay inputs with its exact usage response. This is not native history
replay or Lab startup evidence. The original signed native locator is unchanged;
a successor must independently bind a new installed locator before using it.

Scope is the exact current Linux/x86_64/CPython3.14.4 host. Its standard library
and ABI remain external dependencies, so this is not a portable Python bundle.
Full history/protected-input packaging, cold Lab operation and service ownership
remain pending T07/T08 integration. No credentials, stores or background service
are installed. `installation.json` records copied file hashes and these limits.

Run focused checks from this directory with the selected R02 interpreter:

```
PYTHONDONTWRITEBYTECODE=1 /tmp/cal-R02-environment-0001/bin/python -B -m unittest -v test_preflight test_install
```
