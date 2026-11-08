# LC-U02-05 disposable Mapper guard/refusal candidate, version 0004

This is an **inactive construction candidate** following the versioned
Source→Reader→Mapper read-only 0003 path. It does not use the failed 0002
receipt as input. A future run would recreate Source and Reader in one owned
scratch, hold-read their current manifests, materialize the four Mapper roles
and manifest from those bytes, and complete the read-only Mapper child before
starting a fourth child. No protected Source8 authority or host installation
is implied.

The fourth child mounts the family and selected snapshot read-only. Immediately
before launch, the controller hold-reads the fresh Source, Source package,
Reader, Mapper manifest, and generated `mapped/build.py` bytes; it checks the
whole-family five-leaf Mapper inventory and the mode-0400 selected native copy.
The generated build is statically checked: `guard(pin)` first verifies the
Mapper source and exact native digest; `build(pin)` calls that guard, checks
that `mapped/packages/0001` is absent, then reaches the injected
`_t35_effect_refused()` before package creation or native dispatch. The child
must observe `build.guard(mapper_pin)` succeed and then catch that exact
refusal from `build(mapper_pin)`. Any other exception, normal build return,
stderr, changed inventory, package, or Context path is a failure. The native
copy remains nonexecutable and the selected code has no reachable native call
before the first sealed effect gate.

The child envelope, original process-group closure, unknown-state scratch
retention, cooperative evidence lock, no-replace publication, and 900-second
watchdog are inherited from 0003. The separate result name is
`phase-mapper-build-refusal-result-0004.json`; no preflight or effect has been
run for this candidate. Pure and synthetic tests check the actual generated
build order and runtime refusal with a stubbed source verifier and disposable
native bytes. They do **not** establish that the full fourth child succeeds on
the actual fixture. Independent exact-byte review is required before a
controlled effect attempt.

Even a future PASS would prove only a disposable guard and sealed refusal.
It would not prove Mapper package construction, native invocation, Context,
escaped-session absence, protected host containment, activation, or
LC-U02-05 acceptance. The LC-U03-02 cgroup oracle remains required for actual
protected host qualification.
