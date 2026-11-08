# Disposable exact-bundle importer

`local_import.py` stores exact selected bundle bytes in a private disposable
directory and advances one canonical `HEAD.json` under a local file lock. It
checks selected bytes and the expected prior HEAD, stages and fsyncs the bundle,
then atomically replaces and fsyncs HEAD. A crash after staging leaves an
unpublished bundle that a fresh process can reuse. Exact completed retries are
idempotent; a wrong predecessor, changed bytes, unapproved local state, linked
file or symlinked HEAD refuses. Held directory file descriptors anchor effects
to the originally selected private root and bundle directory. A replaced root
path refuses before staging or HEAD publication; foreign files are untouched.

The `import_decided_bundle` entrypoint accepts only a whole-bundle T26 target
with `local-import` scope and an approved exact-byte state. This is a T27
engineering component, not repository admission. Authenticated owner evidence
and the final T25 bundle must still be selected and reviewed. The
component does not write `authority/` or any canonical Lab store. The focused
tests use temporary roots, including a real child-process crash.
