# Phase-prefix diagnostic successor 0002

Diagnostic-0001 was a static candidate only. Independent review found that a
failure in `TemporaryDirectory.__exit__` would be reported under the preceding
Reader poststate stage. This successor keeps the prior source, test, packet,
and review bytes intact. Its `diagnostic_scratch` context marks `cleanup` only
after the probe body succeeds and before temporary-directory exit. A prior
body failure retains its own stage even if cleanup subsequently raises.

The successor still copies the reviewed 15-leaf Source→Reader prefix logic.
Its failure receipt contains only a closed stage and failure code, each
completed child's bounded return code, stdout/stderr byte lengths and digests,
and post-context scratch absence when observable. It publishes no raw child
output, exception message, fixture path, private signer content, or protected
input. Pure tests simulate cleanup failure, a prior body failure followed by
cleanup failure, oversized child output, timeout, nonzero exit, and sensitive
error text. Normal and optimized suites are required at exact source hashes
before a single diagnostic disposable run.

This is instrumentation to localize the prior intermittent `ContractError`.
It does not establish repeatability by itself or grant Mapper/Context phase
authority, actual WSL host qualification, formal unit acceptance, or activation.
