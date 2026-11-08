# T18 failure custody repair review

Reviewed final `t18-current-service-kill-0001/probe.py`, SHA-256
`2f280dad955a582f5a2a2c44fa16860db7926c182969622b4a7e544556ce57c8`,
against the previously reviewed process-kill probe and its retained preimage.
The native call/OS observer/SIGSTOP/SIGKILL/retry logic is unchanged. The added
context manager removes the owned test root after success and preserves it
after any body failure, retaining the actual original journal bytes.

The initial retention patch could replace the primary failure when writing its
diagnostic marker failed, and could omit the retained-path message. The repair
makes the marker best-effort, always attempts the locator message, and rethrows
the original exception. It does not recreate, alter or infer journal records.

Independently reran all three focused custody tests on the selected native
Python runtime: success cleanup, body failure with original bytes/error/path,
and injected marker-storage failure preserving the primary error and path.
All passed. No remaining blocker was found in this narrow repair. Actual
Service process-kill execution and final selected-package qualification remain
separate; this review does not claim power-loss durability.
