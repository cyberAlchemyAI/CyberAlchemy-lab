# Cold preparation attempt 0002 — selected path refusal

The same no-dispatch cold preparation was retried with `TMPDIR` set to the
task-owned mode-0700 `implementation/lab-runtime/local-host/t31-api52-original-output-0004/working`
directory. Source archive staging passed, then captured runtime
`lab_runtime/store.py:70` refused its own temporary source state:
`RuntimeFault: local runtime state inside repository must live under .local/`.

The task-owned scratch was empty after `TemporaryDirectory` unwound. No
producer request or WorkflowRun append occurred. The next retry uses a new
mode-0700 `.local/t31-api52-source-cold-0004` directory, which is on the main
filesystem and follows that selected engine path rule. The private T31
fixture remains explicitly under `/tmp`.
